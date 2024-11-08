from abc import ABC, abstractmethod
from event_queue import Event, EventQueue
from config import Config
from threading import Lock
import paho.mqtt.client as mqtt
import time
import logging
import random
import datetime
import json
# TODO: Uncomment when working with the Pi
# from picamera2 import Picamera2

class Sensor(ABC):
  def __init__(self, id, type, events_queue):
    # Params
    if not isinstance(id, str):
      raise Exception('Invalid sensor id')
    if not isinstance(type, str):
      raise Exception('Invalid sensor type')
    if not isinstance(events_queue, EventQueue):
      raise Exception('Invalid event queue')
    
    self.id = id
    self.type = type
    self.eventsQueue = events_queue
    
    # Internal
    self.is_active = True
    self.name = f'{type} Sensor {id}'
    # TODO: Uncomment when working with the Pi
    # self.picam2 = Picamera2()
    self.lock = Lock()
    
    # MQTT
    self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.topic = f'/sensor/{self.type.lower()}/{self.id}'
    self.client.on_connect = self.on_connect
    self.client.connect(Config.HOSTNAME, Config.PORT)
    self.client.loop_start()
    
  def on_connect(self, client, userdata, flags, return_code, properties):
    logging.info(f'CONNACK received with code %s.' % return_code)
    if return_code == 0:
        logging.info(f'Connected to MQTT broker')
    else:
        logging.info(f'Failed to connect to MQTT broker', return_code)
        
  def read_event_queue(self):
    while self.is_active:
        event = self.eventsQueue.get_event()
        self.capture(event)
        self.publish_event(event)
  
  @abstractmethod
  def get_sensor_value(self):
      pass
    
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
      humidity_value = self.get_sensor_value()
      motion_event = Event(event_type, event_time, humidity_value)
      
      # Add event to queue
      self.eventsQueue.add_event(motion_event)
      logging.debug(f'EVENT HAPPENED!')
    
  def stop(self):
    self.is_active = False
    self.client.loop_stop()
    
  def capture(self, event):
    if not isinstance(event, Event):
        raise Exception('Invalid event type')
    with self.lock:
        filename = f'{event.type}_{event.time}.jpg'
        # TODO: Implement the capture method
        logging.info(f'Capturing image {filename}')
        time.sleep(1) 
        
  def publish_event(self, event):
    if not isinstance(event, Event):
      raise Exception('Invalid event type')
    data = {
      'id': self.id,
      'name': self.name,
      'type': event.type,
      'time': event.time,
      'data': event.value,
    }
    data = json.dumps(data)
    result = self.client.publish(topic = self.topic, payload = data)
    status = result[0]
    if status == 0:
      logging.info(f'Message sent to topic {self.topic}') 
    else:
      logging.error(f'Failed to send message to topic {self.topic}')
    
