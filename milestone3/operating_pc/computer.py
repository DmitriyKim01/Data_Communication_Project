import logging
import paho.mqtt.client as mqtt

class OperatingComputer:
  def __init__(self, id):
    # Params
    if not isinstance(id, str):
      raise Exception('Invalid id type')
    self.id = id
    self.name = f'Operating Computer {self.id}' 

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
  
    
if __name__ == "__main__":

