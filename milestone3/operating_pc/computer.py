import logging
import paho.mqtt.client as mqtt
import argparse
import grpc
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import proto.sensor_pb2 as sensor_pb2 
import proto.sensor_pb2_grpc as sensor_pb2_grpc
from config import Config
import time
import json
import base64

class OperatingComputer:
    def __init__(self, id, trigger, listen, Type, sensor):
        # Params
        if not isinstance(id, str):
            raise Exception('Invalid id type')
        self.id = id
        self.name = f'Operating Computer {self.id}' 
        if not isinstance(trigger, bool):
            raise Exception('Invalid trigger type')
        if not isinstance(listen, bool):
            raise Exception('Invalid listen type')
        if not isinstance(Type, str):
            raise Exception('Invalid sensor type')
        if not isinstance(sensor, str):
            raise Exception('Invalid sensor id')
        self.trigger = trigger
        self.listen = listen
        self.Type = Type
        self.sensor = sensor
        
        self.is_alive = False
        
        # Logger
        self.logger = logging.getLogger(self.name)
        self.logger = logging.LoggerAdapter(self.logger, {'computer_name': f'{self.name}'})

        # MQTT

        self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.client.on_message = self.on_message
        
        self.topic = f'/operating/computer/{self.id}'
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False

        # gRPC
        self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
        self.stub = sensor_pb2_grpc.SensorServerStub(self.channel)

    def on_connect(self, client, userdata, flags, return_code, properties):
        if return_code == 0:
            self.connected = True
            self.logger.info('Connected to MQTT broker')
        else:
            self.logger.info('Failed to connect to MQTT broker', return_code)
            
    def on_message(self, client, userdata, message):
        # Decode the message payload
        payload= message.payload.decode('utf-8')
        data = json.loads(payload)
        encoded_image = data.get('image')
        if encoded_image:
            # Decode the encoded base64 image
            decoded_image = base64.b64decode(encoded_image)
            data['image'] = decoded_image
        logger.info(f'Received message: {data}')

    # def is_valid_sensor_id(self, sensor_id):
    #     '''Helper method to check if the sensor ID is valid.'''
    #     valid_sensor_ids = self.get_sensor_ids()
    #     if sensor_id not in valid_sensor_ids:
    #         self.logger.error(f'Invalid sensor ID: {sensor_id}. Valid IDs are: {", ".join(valid_sensor_ids)}')
    #         return False
    #     return True

    def listen_to_sensors(self):
        # Connect to MQTT broker
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.client.loop_start()
        while not self.connected:
            self.logger.info('Waiting for MQTT connection...')
            time.sleep(1)
        
        if self.Type.lower() not in [sensor_type.lower() for sensor_type in Config.SENSOR_TYPES]:
            self.logger.error('Invalid sensor type')
            exit(1)

        sensor_id = self.sensor.lower()

        sensor_type = self.Type.lower()
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

    def on_message(self, client, userdata, message):
      """Callback function to handle incoming MQTT messages."""
      print(f"Received message on topic {message.topic}: {message.payload.decode()}")

    def trigger_capture(self):
      # Retrieve valid sensor IDs from the gRPC server
    #   valid_sensor_ids = self.get_sensor_ids()

    #   if not valid_sensor_ids:
    #       self.logger.error('No valid sensor IDs found.')
    #       return
        
      sensor_id = self.sensor.lower()

    #   if not self.is_valid_sensor_id(sensor_id):
    #     self.client.disconnect()
    #     return

      '''Trigger the sensor to capture an image using gRPC.'''
      self.logger.info(f'Triggering capture for sensor {sensor_id}...')
      
      # Create a TriggerRequest object to send to the sensor
      request = sensor_pb2.TriggerRequest(id=sensor_id)

      # Call the TriggerCapture method on the gRPC service
      try:
          response = self.stub.TriggerCapturePc(request)
          # Handle the image data response
          self.logger.info(f'Capture response received from sensor {sensor_id}')
          print(response.image_data)
          self.logger.info(f'Image for sensor {sensor_id} saved successfully.')
      except grpc.RpcError as e:
          self.logger.error(f'Error triggering sensor {sensor_id}: {e.details()}')


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

    # def get_sensor_ids(self):
    #   '''Retrieve all sensor IDs from the gRPC server.'''
    #   try:
    #       response = self.stub.GetSensorIds(sensor_pb2.EmptyRequest())
    #       self.logger.info(f'Retrieved sensor IDs: {response.ids}')
    #       return response.ids
    #   except grpc.RpcError as e:
    #       self.logger.error(f'Error retrieving sensor IDs: {e.details()}')
    #       return []

      
      
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True
      
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # Use `store_true` to create flags that don't require a value
    parser.add_argument('-i', '--id', default='0001', help='Identifies computer')
    parser.add_argument('-t', '--trigger', action='store_true', help='Allows computer to trigger sensors')
    parser.add_argument('-l', '--listen', action='store_true', help='Allows computer to listen to sensors')
    parser.add_argument('-T', '--Type', help='Sensor type')
    parser.add_argument('-s', '--sensor', help='Sensor ID')
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(levelname)s - [{Config.HOSTNAME}:{Config.PORT}] - (%(computer_name)s) - %(message)s'
    )
    
    logger = logging.getLogger()
    logger.addFilter(ComputerNameFilter())
    computer = OperatingComputer(args.id, args.trigger, args.listen, args.Type, args.sensor)
    
    if not args.Type:
        logger.error('Computer must specify a sensor type ( -T | --Type )')
        exit(1)
    if not args.sensor:
        logger.error('Computer must specify a sensor ID ( -s | --sensor )')
        exit(1)
    if not args.trigger and not args.listen:
        logger.error('Computer must specify a trigger flag ( -t | --trigger ) or a listen flag ( -l | --listen )')
        exit(1)

    try:
        computer.start()
    except KeyboardInterrupt:
        computer.disconnect()
