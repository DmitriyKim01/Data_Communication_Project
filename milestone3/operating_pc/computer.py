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

class OperatingComputer:
    def __init__(self, id, trigger, listen):
        # Params
        if not isinstance(id, str):
            raise Exception('Invalid id type')
        self.id = id
        self.name = f'Operating Computer {self.id}' 
        if not isinstance(trigger, bool):
            raise Exception('Invalid trigger type')
        if not isinstance(listen, bool):
            raise Exception('Invalid listen type')
        self.trigger = trigger
        self.listen = listen
        self.is_alive = False
        
        # Logger
        self.logger = logging.getLogger(self.name)
        self.logger = logging.LoggerAdapter(self.logger, {'computer_name': f'{self.name}'})

        # MQTT
        self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
        self.topic = f'/operating/computer/{self.id}'
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.connected = False

        # gRPC
        self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
        self.stub = sensor_pb2_grpc.SensorServiceStub(self.channel)

    def on_connect(self, client, userdata, flags, return_code, properties):
        if return_code == 0:
            self.connected = True
            self.logger.info('Connected to MQTT broker')
        else:
            self.logger.info('Failed to connect to MQTT broker', return_code)
    def on_message(self, client, userdata, message):
        logger.info(f"Received message: {message.payload.decode('utf-8')}")

    def listen_and_trigger(self):
        while True:
            option = input("What do you want to do? Enter (T) for trigger or (L) to listen: ")
            if str.lower(option) == 't':
                self.trigger_capture()
                break
            elif str.lower(option) == 'l':
                self.listen_to_sensors()
                break
            else:
                print("Invalid option. Please enter (T) or (L).")

    def listen_to_sensors(self):
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.client.loop_start()
        sensor_topic = ''
        
        while not self.connected:
            self.logger.info("Waiting for MQTT connection...")
            time.sleep(1)

        sensor_type = Config.validate_options(Config.SENSOR_TYPES, 'Select a sensor type to listen to: ')
        if sensor_type == 'All':
            sensor_topic = '/sensor/#'
        else:
            sensor_id = Config.validate_options(Config.SENSOR_IDS, f'Select a {sensor_type.lower()} sensor ID to listen to: ')
            if sensor_id != 'All':
                sensor_topic = f'/sensor/{sensor_type}/{sensor_id}'
            else:
                sensor_topic = f'/sensor/{sensor_type}/+'
                
        self.client.subscribe(sensor_topic)
        self.logger.info(f"Subscribed to topic: {sensor_topic}")
            
    #   while self.is_alive:
    #       id = input("Enter an IP address (or type 'done' to finish): ")
          
    #       if id.lower() == 'done':
    #           break
    #       # Ensure the user provides a valid sensor type for each IP
    #       while True:
    #           sensor_type = input("Enter sensor type for this IP: (H) for Humidity, (T) for Temperature, (W) for Wind, or (A) for any: ").lower()
    #           if sensor_type in ['h', 't', 'w', 'a']:
    #               break
    #           else:
    #               print("Invalid sensor type. Please enter (H), (T), (W), or (A).")
    #       sensor_details.append((id, sensor_type))  

    #   # Connect to the MQTT broker and start listening
    #   self.client.connect(Config.HOSTNAME, Config.PORT)
    #   self.client.loop_start()

    #   # Subscribe to each topic based on the given IPs and their sensor types
    #   for id, sensor_type in sensor_details:
    #       # Map user input to actual sensor type strings
    #       if sensor_type == "h":
    #           sensor_type = "humidity"
    #       elif sensor_type == "t":
    #           sensor_type = "temperature"
    #       elif sensor_type == "w":
    #           sensor_type = "wind"
    #       else:
    #           sensor_type = "+" 

    #       topic = f'/sensor/{sensor_type}/{id}'
    #       self.client.subscribe(topic)
    #       print(f"Subscribed to topic: {topic}")

    # Keep the program running to listen for incoming messages
    #   try:
    #       while True:
    #           if self.listen and not self.trigger:
    #               pass
    #           else:
    #               self.act()  
    #   except KeyboardInterrupt:
    #       self.disconnect()
    #       print("Disconnected from MQTT broker.")


    def trigger_capture(self):
      # Retrieve valid sensor IDs from the gRPC server
      valid_sensor_ids = self.get_sensor_ids()

      if not valid_sensor_ids:
          self.logger.error("No valid sensor IDs found.")
          return
      sensor_id = ""

      # Keep asking for a sensor ID until the user provides a valid one
      while True:
          sensor_id = input("Enter a sensor ID to trigger: ")
          if sensor_id in valid_sensor_ids:
              break
          else:
              print(f"Invalid sensor ID. Valid IDs are: {', '.join(valid_sensor_ids)}")

      """Trigger the sensor to capture an image using gRPC."""
      self.logger.info(f'Triggering capture for sensor {sensor_id}...')
      
      # Create a TriggerRequest object to send to the sensor
      request = sensor_pb2.TriggerRequest(sensor_id=sensor_id)

      # Call the TriggerCapture method on the gRPC service
      try:
          response = self.stub.TriggerCapture(request)
          # Handle the image data response
          self.logger.info(f"Capture response received from sensor {sensor_id}")
          print(response.image_data)
          self.logger.info(f"Image for sensor {sensor_id} saved successfully.")
      except grpc.RpcError as e:
          self.logger.error(f"Error triggering sensor {sensor_id}: {e.details()}")


    def start(self):
        self.is_alive = True
        
        if self.trigger and self.listen:
            self.listen_and_trigger()
        elif self.trigger and not self.listen:
            self.trigger_capture()
        else:
            self.listen_to_sensors()
        while True:
            time.sleep(1)

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def get_sensor_ids(self):
      """Retrieve all sensor IDs from the gRPC server."""
      try:
          response = self.stub.GetSensorIds(sensor_pb2.EmptyRequest())
          self.logger.info(f"Retrieved sensor IDs: {response.ids}")
          return response.ids
      except grpc.RpcError as e:
          self.logger.error(f"Error retrieving sensor IDs: {e.details()}")
          return []
      
      
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True
      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Use `store_true` to create flags that don't require a value
    parser.add_argument('-i', '--id', default="0001", help="Identifies computer")
    parser.add_argument('-t', '--trigger', action='store_true', help="Allows computer to trigger sensors")
    parser.add_argument('-l', '--listen', action='store_true', help="Allows computer to listen to sensors")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(levelname)s - [{Config.HOSTNAME}:{Config.PORT}] - (%(computer_name)s) - %(message)s'
    )
    
    logger = logging.getLogger()
    logger.addFilter(ComputerNameFilter())
    computer = OperatingComputer(args.id, args.trigger, args.listen)
    
    if not args.trigger and not args.listen:
        logger.error('Computer must either --trigger or --listen to sensors')
        exit(1)
    try:
        computer.start()
    except KeyboardInterrupt:
        computer.disconnect()
