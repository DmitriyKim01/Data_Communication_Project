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

class OperatingComputer:
    def __init__(self, id, trigger, listen):
        # Params
        if not isinstance(id, str):
            raise Exception('Invalid id type')
        self.id = id
        self.name = f'Operating Computer {self.id}' 
        self.trigger = trigger
        self.listen = listen

        # Logger
        self.logger = logging.getLogger(self.name)
        self.logger = logging.LoggerAdapter(self.logger, {'sensor_name': f'OC {self.id}'})

        # MQTT

        self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
        self.client.connect(Config.HOSTNAME, Config.PORT)
        self.client.on_message = self.on_message
        

        # gRPC
        self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
        self.stub = sensor_pb2_grpc.SensorServiceStub(self.channel)

    def on_connect(self, client, userdata, flags, return_code, properties):
        if return_code == 0:
            self.logger.info('Connected to MQTT broker')
        else:
            self.logger.info('Failed to connect to MQTT broker', return_code)

    def handle_actions(self):
        while True:
            option = input("What do you want to do? Enter (T) for trigger or (L) to listen: ")
            if str.lower(option) == 't':
                self.trigger_sensor()
                break
            elif str.lower(option) == 'l':
                self.listen_to_sensors()
                break
            else:
                print("Invalid option. Please enter (T) or (L).")

    def listen_to_sensors(self):
      # Collect multiple sensors
      print("Currently selecting which sensors to listen to...")
      sensor_details = [] 
   
      while True:
          id = input("Enter an ID of sensor: ")
          
          if id.lower() == 'done':
              break
          # Ensure the user provides a valid sensor type for each IP
          while True:
              sensor_type = input("Enter sensor type for this IP: (H) for Humidity, (T) for Temperature, (W) for Wind, or (A) for any: ").lower()
              if sensor_type in ['h', 't', 'w', 'a']:
                  break
              else:
                  print("Invalid sensor type. Please enter (H), (T), (W), or (A).")
          sensor_details.append((id, sensor_type))  
        # Subscribe to each topic based on the given IPs and their sensor types
          for id, sensor_type in sensor_details:
              # Map user input to actual sensor type strings
              if sensor_type == "h":
                  sensor_type = "humidity"
              elif sensor_type == "t":
                  sensor_type = "temperature"
              elif sensor_type == "w":
                  sensor_type = "wind"
              else:
                  sensor_type = "+" 
              self.client.subscribe(f'/sensor/{sensor_type}/{id}')
              
      # Connect to the MQTT broker and start listening
      self.client.loop_start()

    # Keep the program running to listen for incoming messages
      try:
          while True:
              if self.listen and not self.trigger:
                  pass
              else:
                  self.act()  
      except KeyboardInterrupt:
          self.disconnect()
          print("Disconnected from MQTT broker.")

    def on_message(self, client, userdata, message):
      """Callback function to handle incoming MQTT messages."""
      print(f"Received message on topic {message.topic}: {message.payload.decode()}")

    def trigger_sensor(self):
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



    def act(self):
        if self.trigger and self.listen:
            self.handle_actions()
        elif self.trigger and not self.listen:
            self.trigger_sensor()
        else:
            self.listen_to_sensors()

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

      
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # Use `store_true` to create flags that don't require a value
    parser.add_argument('-i', '--id', default="0001", help="Identifies computer")
    parser.add_argument('-t', '--trigger', action='store_true', help="Allows computer to trigger sensors")
    parser.add_argument('-l', '--listen', action='store_true', help="Allows computer to listen to sensors")
    
    args = parser.parse_args()

    computer = OperatingComputer(args.id, args.trigger, args.listen)
    try:
        computer.act()
    except KeyboardInterrupt:
        computer.disconnect()
