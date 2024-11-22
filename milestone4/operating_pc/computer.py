
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
        
    def start(self):
        self.is_alive = True
        
        if self.trigger and self.listen:
            self.logger.info("Triggering and Listening sensors")
            self.trigger_capture()
            self.listen_to_sensors()
        elif self.trigger and not self.listen:
            self.logger.info("Triggering sensors")
            self.trigger_capture()
        else:
            self.logger.info("Listening to sensors")
            self.listen_to_sensors()
        while True:
            time.sleep(1)

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
                return self.log[-1]  
            else:
                return None 

        
    def listen_to_sensors(self):
        
        # Connect to MQTT broker
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.connected = True

        self.client.loop_start()
        while not self.connected:
            self.logger.info('Waiting for MQTT connection...')
            time.sleep(1)
        
        if self.type.lower() not in [sensor_type.lower() for sensor_type in Config.SENSOR_TYPES]:
            self.logger.error('Invalid sensor type')
            exit(1)

        sensor_id = self.sensor.lower()

        sensor_type = self.type.lower()
        if not self.is_valid_sensor_id(sensor_id):
            self.client.disconnect()
            return
        
        sensor_topic = self.validate_sensor_topic(sensor_type, sensor_id)
        self.client.subscribe(sensor_topic)
        self.logger.info(f'Subscribed to topic: {sensor_topic}')
        
    def validate_sensor_topic(self, sensor_type, sensor_id):
        sensor_topic = ''
        # Subscribe to any sensor topic
        if sensor_type == 'all' and sensor_id == 'all':
            sensor_topic = '/sensor/#'
        # Subscribe to all sensors with a specific id
        elif sensor_type == 'all' and sensor_id != 'all':
            sensor_topic = f'/sensor/+/{sensor_id}'
        # Subscribe to all sensors of a specific type
        elif sensor_type != 'all' and sensor_id == 'all':
            sensor_topic = f'/sensor/{sensor_type}/+'
        # Subscribe to a specific sensor
        else:
            sensor_topic = f'/sensor/{sensor_type}/{sensor_id}'
        return sensor_topic

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
        valid_sensor_ids = self.get_sensor_ids()
        if sensor_id not in valid_sensor_ids:
            self.logger.error(f'Invalid sensor ID: {sensor_id}. Valid IDs are: {", ".join(valid_sensor_ids)}')
            return False
        return True

# Filter for logging
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True
      

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', default='0001', help='Identifies computer')
    parser.add_argument('-t', '--trigger', action='store_true', help='Allows computer to trigger sensors')
    parser.add_argument('-l', '--listen', action='store_true', help='Allows computer to listen to sensors')
    parser.add_argument('-T', '--type', help='Sensor type')
    parser.add_argument('-s', '--sensor', help='Sensor ID')
    parser.add_argument('-a', '--all', action='store_true', help="Returns a list of available ids to trigger.")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(levelname)s - [{Config.HOSTNAME}:{Config.PORT}] - (%(computer_name)s) - %(message)s'
    )
    logger = logging.getLogger()
    logger.addFilter(ComputerNameFilter())

    # If -a is used, display available sensor IDs but don't exit
    if args.all:
        computer = OperatingComputer(args.id, False, False, '', '')
        available_ids = computer.get_sensor_ids()
        logger.info(f"Available Sensor Ids are {available_ids}")
    
    # Check if required arguments are passed for normal operation
    if not args.type:
        logger.error('Computer must specify a sensor type ( -T | --type )')
        exit(1)
    if not args.sensor:
        logger.error('Computer must specify a sensor ID ( -s | --sensor )')
        exit(1)
    if not args.trigger and not args.listen:
        logger.error('Computer must specify a trigger flag ( -t | --trigger ) or a listen flag ( -l | --listen )')
        exit(1)

    # Create a new computer instance
    computer = OperatingComputer(args.id, args.trigger, args.listen, args.type, args.sensor)
    
    try:
        computer.start()
    except KeyboardInterrupt:
        logger.warning("Keyboard interruption trapped. Shutting down...")
        computer.disconnect()
        logger.info("Shutdown complete.")
