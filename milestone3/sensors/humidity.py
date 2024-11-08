from config import HOSTNAME, PORT
import paho.mqtt.client as mqtt
import argparse
import random

class HumiditySensor:
  def __init__(self, id):
    self.id = id
    self.is_active = True
    
    # MQTT
    self.client = mqtt.Client(client_id=f'Humidity Sensor {self.id}', callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.topic = f'/sensor/humidity/{self.id}'
    self.client.on_connect = self.on_connect
    self.client.connect(HOSTNAME, PORT)
  
  def on_connect(self, client, userdata, flags, return_code, properties):
    print(f'(Humidity Sensor {self.id})[CONNACK] received with code %s.' % return_code)
    if return_code == 0:
        print(f'(Humidity Sensor {self.id})[CONNECTED] to {HOSTNAME} on port {PORT}')
    else:
        print(f'(Humidity Sensor {self.id})[CONNECTION ERROR] to {HOSTNAME} on port {PORT}', return_code)
  
  def simulate_motion_detection(self):
    with self.is_active:
        sleep(random)
        
        






  if __name__ == "__main__":
      parser = argparse.ArgumentParser()
      parser.add_argument('-l', '--lat_long',nargs=2, default=[45.5,73.5])
      parser.add_argument('-c', '--city', default="Montreal")
      parser.add_argument('-i', '--id', default="0001")
      parser.add_argument('-t', '--test', action='store_true')
      args = parser.parse_args()
    
        
