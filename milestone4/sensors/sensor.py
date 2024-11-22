
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from abc import ABC, abstractmethod
from event import Event
from config import Config
from threading import Lock, Thread
import os
import paho.mqtt.client as mqtt
import base64
import time
import logging
import random
import datetime
import json
import grpc
from concurrent import futures
from proto import sensor_pb2
from proto import sensor_pb2_grpc as grpc_sensor
from PIL import Image
import io

class Sensor(grpc_sensor.SingleSensor):
  def __init__(self, id: str, port: int):
    # Params
    self.id = id
    self.port = port
    # Internal
    self.is_active = True
    self.name = f'Sensor {id}' 
    self.threads = []
    self.ip = "localhost"
    
    # Logger
    self.logger = logging.getLogger(self.name)
    self.logger = logging.LoggerAdapter(self.logger, {'sensor_name': f'Sensor {self.id}'})
    self.lock = Lock()
    
    # MQTT
    self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.client.on_connect = self.on_connect

    # GRPC
    self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
    self.stub = grpc_sensor.SensorServerStub(self.channel)
  
  
  def start(self):
    self.is_active = True
    # Connect to MQTT broker
    self.client.connect(Config.HOSTNAME, Config.PORT)
    self.client.loop_start()
    
    # Simulate motion detection
    motion_simulation_thread = Thread(target=self.simulate_motion)
    self.threads.append(motion_simulation_thread)
    motion_simulation_thread.start()

    # Start the GRPC server
    self.send_address_to_server()
    start_server_thread = Thread(target=self.serve)
    self.threads.append(start_server_thread)
    start_server_thread.start()
    
  def stop(self):
    # Stop any sensor's loops
    self.is_active = False
    # Stop the MQTT client
    self.client.loop_stop()
    # Stop any threads on the sensor
    for thread in self.threads:
      if not isinstance(thread, Thread):
        raise Exception('Invalid thread type')
      thread.join(timeout=1)
    # Stop the gRPC server
    if self.server:
      self.logger.warning(f"Stopping GRPC server. Please wait...")
      self.server.stop(grace=None)  
      self.logger.warning(f"GRPC server stopped.")
    if self.channel:
      self.channel.close()
      self.logger.warning(f'Closed GRPC channel')
      
  # MOTION SIMULATION METHODS -----------------------------
        
  # Simulate motion detection
  def simulate_motion(self):
    while self.is_active:
      # Simulate motion detection
      min_interval = Config.EVENT_MIN_INTERVAL
      max_interval = Config.EVENT_MAX_INTERVAL
      random_inteval = random.uniform(min_interval, max_interval)
      time.sleep(random_inteval)
      
      temperature = self.get_temperature()
      wind = self.get_wind()
      humidity = self.get_humidity()
      
      # Publish event to MQTT broker
      self.logger.info(f'MOTION EVENT HAPPENED')
      image = self.capture_event()
      self.publish_image(image)
      self.publish_temperature(temperature)
      self.publish_wind(wind)
      self.publish_humidity(humidity)
      self.publish_all(humidity, temperature, wind)
      
  # MQTT METHODS -----------------------------
  
  # Triggered when the sensor connects to the MQTT broker
  def on_connect(self, client, userdata, flags, return_code, properties):
    if return_code == 0:
        self.logger.info(f'Connected to MQTT broker')
    else:
        self.logger.info(f'Failed to connect to MQTT broker', return_code)  
  
  def publish_image(self, image: bytes):
     # Serialize the byte array using base64 encoding
    encoded_image = base64.b64encode(image).decode('utf-8')
    data = {
      'id': self.id,
      'name': self.name,
      'type': 'image',
      'image': encoded_image
    }
    data = json.dumps(data)
    topic = f'/sensor/image/{self.id}'
    result = self.client.publish(topic = topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {topic}')

  def publish_temperature(self, temperature: int):
    data = {
      'id': self.id,
      'name': self.name,
       'type': 'temperature',
      'temperature': temperature
    }
    data = json.dumps(data)
    topic = f'/sensor/temp/{self.id}'
    result = self.client.publish(topic = topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {topic}')
  
  def publish_wind(self, wind: int):
    data = {
      'id': self.id,
      'name': self.name,
      'type': 'wind',
      'wind': wind
    }
    data = json.dumps(data)
    topic = f'/sensor/wind/{self.id}'
    result = self.client.publish(topic = topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {topic}')
      
  def publish_humidity(self, humidity: int):
    data = {
      'id': self.id,
      'name': self.name,
      'type': 'humidity',
      'humidity': humidity
    }
    data = json.dumps(data)
    topic = f'/sensor/humidity/{self.id}'
    result = self.client.publish(topic = topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {topic}')
  
  def publish_all(self, humidity: int, temperature: int, wind: int):
    data = {
      'id': self.id,
      'name': self.name,
      'type': 'all',
      'humidity': humidity,
      'temperature': temperature,
      'wind': wind
    }
    data = json.dumps(data)
    topic = f'/sensor/all/{self.id}'
    result = self.client.publish(topic = topic, payload = data)
    status = result[0]
    if status == 0:
      self.logger.info(f'Message sent to topic {topic}') 
    else:
      self.logger.error(f'Failed to send message to topic {topic}')
  
  # VALUE METHODS -----------------------------
  
  def get_humidity(self):
    return random.uniform(Config.HUMIDITY_MIN_VALUE, Config.HUMIDITY_MAX_VALUE)
  def get_temperature(self):
    return random.uniform(Config.TEMPERATURE_MIN_VALUE, Config.TEMPERATURE_MAX_VALUE)
  def get_wind(self):
    return random.uniform(Config.WIND_MIN_VALUE, Config.WIND_MAX_VALUE)

  # GRPC METHODS -----------------------------
  
  # Starts the GRPC server
  def serve(self):
    grpc_sensor.add_SingleSensorServicer_to_server(self, self.server)
    self.server.add_insecure_port(f'[::]:{self.port}')
    self.logger.info(f"Starting GRPC server on address: {Config.GRPC_SERVER_ADDRESS}")
    self.server.start()
    self.server.wait_for_termination()

  # Sends the sensor id, ip, and port to the GRPC server
  def send_address_to_server(self):
    try:
      request = sensor_pb2.SensorInfo(id=self.id,ip = self.ip, port = self.port)
      response = self.stub.AddSensor(request)
    except grpc.RpcError as e:
      self.logger.error(f'Error triggering sensor {e.details()}')
  
  # Triggered when the GRPC server receives a request to capture an image
  def TriggerCapture(self, request, context):
    sensor_id = request.id
    # Ensure the sensor exists
    if sensor_id != self.id:
      context.set_code(grpc.StatusCode.NOT_FOUND)
      return sensor_pb2.CaptureResponse() 
    try:
        image_data = self.capture_event()  
        return sensor_pb2.CaptureResponse(image_data=image_data)
    except Exception as e:
        context.set_details(f"Error capturing image: {e}")
        context.set_code(grpc.StatusCode.INTERNAL)
        return sensor_pb2.CaptureResponse()
  
  # CAMERA METHODS -----------------------------
  
  # Return random byte array as an image
  def capture_event(self):
    with self.lock:
      with open(os.path.abspath(os.path.join(os.path.dirname(__file__), './f1.jpg')), "rb") as image_file:
        image = Image.open(image_file)
        byte_array = io.BytesIO()
        image.save(byte_array, format=image.format)
        return byte_array.getvalue()
  


