import logging
import paho.mqtt.client as mqtt
import argparse

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

  def act(self):
    pass 
  
  def disconnect(self):
      self.client.loop_stop()
      self.client.disconnect()

    


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    
    # Use `store_true` to create flags that don't require a value
    parser.add_argument('-t', '--trigger', action='store_true', help="Allows computer to trigger sensors")
    parser.add_argument('-l', '--listen', action='store_true', help="Allows computer to listen to sensors")
    
    args = parser.parse_args()


   
    computer = OperatingComputer()
    try:
        while True:
          computer.act()
    except KeyboardInterrupt:
        computer.disconnect()
