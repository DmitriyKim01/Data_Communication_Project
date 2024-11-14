from abc import ABC, abstractmethod
from event_queue import Event, EventQueue
from config import Config
from threading import Lock, Thread
import paho.mqtt.client as mqtt
import base64
import time
import logging
import random
import datetime
import json
import os
# TODO: Uncomment when working with the Pi
# from picamera2 import Picamera2

class Sensor(ABC):
  def __init__(self, id, type):
    # Params validation
    if not isinstance(id, str):
      raise Exception('Invalid sensor id')
    if not isinstance(type, str):
      raise Exception('Invalid sensor type')
    # Params
    self.id = id
    self.type = type
    
    # Internal
    self.is_active = True
    self.name = f'{type} Sensor {id}' 
    self.eventsQueue = EventQueue()
    self.threads = []
    
    # Logger
    self.logger = logging.getLogger(self.name)
    self.logger = logging.LoggerAdapter(self.logger, {'sensor_name': f'{self.type[0:3]}. Sensor {self.id}'})
  
    # TODO: Uncomment when working with the Pi
    # self.picam2 = Picamera2()
    self.lock = Lock()
    
    # MQTT
    self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.topic = f'/sensor/{self.type.lower()}/{self.id}'
    self.client.on_connect = self.on_connect
  
  def start(self):
    # Connect to MQTT broker
    self.client.connect(Config.HOSTNAME, Config.PORT)
    self.client.loop_start()
    
    # Simulate motion detection
    motion_simulation_thread = Thread(target=self.simulate_motion)
    self.threads.append(motion_simulation_thread)
    motion_simulation_thread.start()
    
    # Read event queue
    read_event_queue_thread = Thread(target=self.read_event_queue)
    self.threads.append(read_event_queue_thread)
    read_event_queue_thread.start()
    
    
  def on_connect(self, client, userdata, flags, return_code, properties):
    if return_code == 0:
        self.logger.info(f'Connected to MQTT broker')
    else:
        self.logger.info(f'Failed to connect to MQTT broker', return_code)
  
  # TODO: Implement the read_event_queue method
  def read_event_queue(self):
    while self.is_active:
        event = self.eventsQueue.get_event()
        image= self.capture_event(event)
        self.publish_event(event, image)
  
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
      self.logger.info(f'MOTION EVENT HAPPENED')
    
  def stop(self):
    self.is_active = False
    self.client.loop_stop()
    for thread in self.threads:
      if not isinstance(thread, Thread):
        raise Exception('Invalid thread type')
      thread.join(timeout=1)
      time.sleep(1)  
  
  def capture_event(self, event):
    if not isinstance(event, Event):
        raise Exception('Invalid event type')
    with self.lock:
        filename = f'{event.type}_{event.time}.jpg'
        # The byte array is set to 4 bytes for testing purposes
        image = os.urandom(4)
        self.logger.info(f'Capturing image {filename}')
        return image
        
  def capture(self):
    # Simulate image capture
    # The byte array is set to 4 bytes for testing purposes
    image = os.urandom(4)
    self.logger.info(image)
    return image
   
  def publish_event(self, event, image):
    if not isinstance(event, Event):
      raise Exception('Invalid event type')
    if not isinstance(image, bytes):
      raise Exception('Invalid image type')
     # Serialize the byte array using base64 encoding
    encoded_image = base64.b64encode(image).decode('utf-8')
    data = {
      'id': self.id,
      'name': self.name,
      'type': event.type,
      'time': event.time,
      'data': event.value,
      'image': encoded_image
    }
    data = json.dumps(data)
    result = self.client.publish(topic = self.topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {self.topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {self.topic}')
      
  @abstractmethod
  def get_sensor_value(self):
      pass
    
    
