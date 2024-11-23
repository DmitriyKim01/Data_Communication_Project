
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import logging
import paho.mqtt.client as mqtt
import argparse
import grpc
import proto.sensor_pb2 as sensor_pb2 
import proto.sensor_pb2_grpc as sensor_pb2_grpc
from config import Config
import time
import json
import base64
import threading
class OperatingComputer:
    def __init__(self, id, trigger, listen, type, sensor):
        # Params
        if not isinstance(id, str):
            raise Exception('Invalid id type')
        self.id = id
        self.name = f'Operating Computer {self.id}'
        if not isinstance(trigger, bool):
            raise Exception('Invalid trigger type')
        if not isinstance(listen, bool):
            raise Exception('Invalid listen type')
        if not isinstance(type, str):
            raise Exception('Invalid sensor type')
        if not isinstance(sensor, str):
            raise Exception('Invalid sensor id')
        
        self.trigger = trigger
        self.listen = listen
        self.type = type
        self.sensor = sensor
        self.is_alive = False
        
        # Logger
        self.logger = logging.getLogger(self.name)
        self.logger = logging.LoggerAdapter(self.logger, {'computer_name': f'{self.name}'})

        # MQTT
        self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False
        self.log = []
        self.log_lock = threading.Lock()
        # gRPC
        self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
        self.stub = sensor_pb2_grpc.SensorServerStub(self.channel)
        self.subscribed_topics = set()

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        self.is_alive = False
        
    # MQTT ----------------------------------------------------------------
    def on_connect(self, client, userdata, flags, return_code, properties):
        if return_code == 0:
            self.connected = True
            self.logger.info('Connected to MQTT broker')
        else:
            self.logger.info('Failed to connect to MQTT broker', return_code)
            
    def on_message(self, client, userdata, message):
        payload = message.payload.decode('utf-8')
        data = json.loads(payload)
        encoded_image = data.get('image')
        if encoded_image:
            with self.log_lock:
                self.log.append(f"Received data from sensor : {self.sensor} at {time.ctime()}")

    def get_log(self):
        with self.log_lock:
            if len(self.log) > 0:
                return self.log 
            else:
                return None 
    def clear_log(self):
        with self.log_lock:
            if len(self.log) >0:
                self.log.clear()

        
    def listen_to_sensors(self, sensor_type, sensor_id):
        try:
            # Ensure client is connected
            if not self.connected:
                self.client.connect(Config.HOSTNAME, Config.PORT)
                self.client.loop_start()

                # Wait for connection with timeout
                start_time = time.time()
                while not self.connected:
                    if time.time() - start_time > Config.CONNECTION_TIMEOUT:
                        self.logger.error("MQTT connection timed out.")
                        self.client.loop_stop()
                        return False
                    time.sleep(0.1)

            # Validate sensor type
            valid_types = [st.lower() for st in Config.SENSOR_TYPES]
            if sensor_type.lower() not in valid_types:
                self.logger.error(f"Invalid sensor type: {sensor_type}")
                return False

            # Validate sensor ID
            if not self.is_valid_sensor_id(sensor_id):
                return False

            # Convert to lowercase and construct the topic
            topic = f"/sensor/{sensor_type.lower()}/{sensor_id.lower()}"

            # Append to subscribed topics if not already subscribed
            if not hasattr(self, 'subscribed_topics'):
                self.subscribed_topics = set() 

            if topic not in self.subscribed_topics:
                self.client.subscribe(topic)
                self.subscribed_topics.add(topic)
                self.logger.info(f"Successfully subscribed to topic: {topic}")
            else:
                self.logger.info(f"Already subscribed to topic: {topic}")

            return True
        except Exception as e:
            self.logger.error(f"Error in listen_to_sensors: {e}")
            return False


    # GRPC ----------------------------------------------------------------
    
    # Trigger the sensor to capture an image    
    def trigger_capture(self):
        sensor_id = self.sensor.lower()

        '''Trigger the sensor to capture an image using gRPC.'''
        self.logger.info(f'Triggering capture for sensor {sensor_id}...')

        # Create a TriggerRequest object to send to the sensor
        request = sensor_pb2.TriggerRequest(id=sensor_id)

        # Call the TriggerCapture method on the gRPC service
        try:
            response = self.stub.TriggerCapturePc(request)
            # Handle the image data response
            self.logger.info(f'Capture response received from sensor {sensor_id}')
            self.logger.info(f'{response.image_data}')
            self.logger.info(f'Image for sensor {sensor_id} saved successfully.')
        except grpc.RpcError as e:
            self.logger.error(f'Error triggering sensor {sensor_id}: {e.details()}')

    # HELPER METHODS ----------------------------------------------------------------
    def get_sensor_ids(self):
        """Fetch and return all available sensor IDs from the gRPC server."""
        try:
            # Call the GetSensorIds method to get the list of sensor IDs
            response = self.stub.GetSensorIds(sensor_pb2.EmptyRequest())
            sensor_ids = [sensor_id for sensor_id in response.ids]
            self.logger.info('Available sensor IDs:')
            return sensor_ids
        except grpc.RpcError as e:
            self.logger.error(f'Error fetching sensor IDs: {e.details()}')
            return []

    def is_valid_sensor_id(self, sensor_id):
        '''Helper method to check if the sensor ID is valid.'''
        if sensor_id == "+":
            return True
        valid_sensor_ids = self.get_sensor_ids()
        if sensor_id not in valid_sensor_ids:
            self.logger.error(f'Invalid sensor ID: {sensor_id}. Valid IDs are: {", ".join(valid_sensor_ids)}')
            return False
        return True




