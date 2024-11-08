from config import Config
import paho.mqtt.client as mqtt
from threading import Thread, Lock
from event_queue import Event, EventQueue
import argparse
import random
import datetime
import time
import logging

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
    self.client.connect(Config.HOSTNAME, Config.PORT)
    self.client.loop_start()
  
  def on_connect(self, client, userdata, flags, return_code, properties):
    print(f'{self.name}[CONNACK] received with code %s.' % return_code)
    if return_code == 0:
        print(f'{self.name}[CONNECTED] to {Config.HOSTNAME} on port {Config.PORT}')
    else:
        print(f'{self.name}[CONNECTION ERROR] to {Config.HOSTNAME} on port {Config.PORT}', return_code)
  
  def simulate_motion_detection(self):
    with self.is_active:
        time.sleep(random)
        
  def read_event_queue(self):
    while self.is_active:
        event = self.eventsQueue.get_event()
        print(f'{self.name}[EVENT] {event}')
        self.client.publish(self.topic, event)
  
  def simulate_motion(self):
    while self.is_active:
      # Simulate motion detection
      min_interval = Config.EVENT_MIN_INTERVAL
      max_interval = Config.EVENT_MAX_INTERVAL
      random_inteval = random.uniform(min_interval, max_interval)
      time.sleep(random_inteval)
      
      # Create new event
      event_type = Config.EVENT_TYPE
      event_time = datetime.datetime.now().strftime(Config.DATE_FORMAT)
      humidity_value = random.uniform(Config.HUMIDITY_MIN_VALUE, Config.HUMIDITY_MAX_VALUE)
      motion_event = Event(event_type, event_time, humidity_value)
      
      # Add event to queue
      self.eventsQueue.add_event(motion_event)
      print(f'{self.name}[EVENT] {motion_event}')
    
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
  
  # Threads
  motion_simulation_thread = Thread(target=sensor.simulate_motion)
  
  if args.test:
    try:
      motion_simulation_thread.start()
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      logging.warning("Keyboard interruption trapped. Shutting down...")
    except Exception as e:
      logging.error(e)
    finally:
      sensor.is_active = False
      sensor.client.loop_stop()
      motion_simulation_thread.join(timeout=1)
      time.sleep(1)
      print("Done...")

      
    
        
