import logging
import paho.mqtt.client as mqtt
import argparse
from config import Config

class OperatingComputer:
  def __init__(self, id, trigger,listen):
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
    self.topic = f'/operating/computer/{self.id}'
    self.client.on_connect = self.on_connect

  def on_connect(self, client, userdata, flags, return_code, properties):
    if return_code == 0:
        self.logger.info(f'Connected to MQTT broker')
    else:
        self.logger.info(f'Failed to connect to MQTT broker', return_code)

  def handle_actions(self):
        self.logger.info('Handling both triggering and listening to sensors...')
        self.listen_to_sensor()

  def listen_to_sensors(self):
      # TODO: MAKE THIS AUTOMATIC SOMEHOW
      # Collect multiple IP addresses from the user
      ids = []
      while True:
          id = input("Enter an IP address (or type 'done' to finish): ")
          if id.lower() == 'done':
              break
          ids.append(id)

      sensor_type = input("Enter sensor type: ")
      self.client.connect(Config.HOSTNAME, Config.PORT)
      self.client.loop_start()
      # Subscribe to each topic for the given IPs
      for id in ids:
          topic = f'/sensor/{sensor_type}/{id}'
          self.client.subscribe(topic)
          print(f"Subscribed to topic: {topic}")



  def trigger_sensor(self):
        # Handle triggering a sensor (simulating sending an event or command to a sensor)
        self.logger.info('Triggering sensor...')
        # Simulate sending a command to the sensor via MQTT (or any other mechanism)
        self.client.publish(self.topic, "Trigger command to sensor")

  def act(self):
      if(self.trigger and self.listen):
        self.handle_actions()
      elif(self.trigger and not self.listen):
        self.trigger_sensor()
      else:
        self.listen_to_sensors()
    

  
  def disconnect(self):
      self.client.loop_stop()
      self.client.disconnect()

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # Use `store_true` to create flags that don't require a value
    parser.add_argument('-i', '--id', default="0001", help="Identifies computer")
    parser.add_argument('-t', '--trigger', action='store_true', help="Allows computer to trigger sensors")
    parser.add_argument('-l', '--listen', action='store_true', help="Allows computer to listen to sensors")
    
    args = parser.parse_args()


   
    computer = OperatingComputer(args.id,args.trigger,args.listen)
    try:
        computer.act()
    except KeyboardInterrupt:
        computer.disconnect()
