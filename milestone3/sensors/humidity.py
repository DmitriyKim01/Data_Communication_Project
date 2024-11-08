from config import HOSTNAME, PORT, EVENT_MIN_INTERVAL, EVENT_MAX_INTERVAL
import paho.mqtt.client as mqtt
from milestone3.sensors.event_queue import Event, EventQueue
import argparse
import random
import datetime
import time

class HumiditySensor:
  def __init__(self, id, eventsQueue):
    # Params
    self.id = id
    if not isinstance(eventsQueue, EventQueue):
        raise Exception('Invalid event queue')
    self.eventsQueue = eventsQueue
    
    # Internal
    self.is_active = True
    self.name = f'(Humidity Sensor {self.id})'
    
    # MQTT
    self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.topic = f'/sensor/humidity/{self.id}'
    self.client.on_connect = self.on_connect
    self.client.connect(HOSTNAME, PORT)
    self.client.loop_start()
  
  def on_connect(self, client, userdata, flags, return_code, properties):
    print(f'{self.name}[CONNACK] received with code %s.' % return_code)
    if return_code == 0:
        print(f'{self.name}[CONNECTED] to {HOSTNAME} on port {PORT}')
    else:
        print(f'{self.name}[CONNECTION ERROR] to {HOSTNAME} on port {PORT}', return_code)
  
  def simulate_motion_detection(self):
    with self.is_active:
        time.sleep(random)
        
  def read_event_queue(self):
    while self.is_active:
        event = self.eventsQueue.get_event()
        print(f'{self.name}[EVENT] {event}')
        self.client.publish(self.topic, event)
        
  # def capture(self):

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--lat_long',nargs=2, default=[45.5,73.5])
    parser.add_argument('-c', '--city', default="Montreal")
    parser.add_argument('-i', '--id', default="0001")
    parser.add_argument('-t', '--test', action='store_true')
    args = parser.parse_args()
    
    eventsQueue = EventQueue()
    sensor = HumiditySensor(args.id, eventsQueue)
    
    if args.test:
      while True:
        time.sleep(random.uniform(EVENT_MIN_INTERVAL, EVENT_MAX_INTERVAL))
        event_type = 'motion'
        event_time = datetime.datetime.now().strftime('%Y-%m-%d_%Hh-%Mm-%Ss')
        motion_event = Event(event_type, event_time)
        sensor.eventsQueue.add_event(motion_event)
    
        
