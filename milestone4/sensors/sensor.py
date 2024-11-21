
from abc import ABC, abstractmethod
from event_queue import Event, EventQueue
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
import proto.sensor_pb2 as sensor_pb2
import proto.sensor_pb2_grpc as grpc_sensor

class Sensor(grpc_sensor.SingleSensor,ABC):
  def __init__(self, id, type, port):
    # Params validation
    if not isinstance(id, str):
      raise Exception('Invalid sensor id')
    if not isinstance(type, str):
      raise Exception('Invalid sensor type')
    if not isinstance(port, int):
      raise Exception('Invalid port number')
    # Params
    self.id = id
    self.type = type
    self.port = port
    # Internal
    self.is_active = True
    self.name = f'{type} Sensor {id}' 
    self.eventsQueue = EventQueue()
    self.threads = []
    self.ip = "localhost"
    
    # Logger
    self.logger = logging.getLogger(self.name)
    self.logger = logging.LoggerAdapter(self.logger, {'sensor_name': f'{self.type[0:3]}. Sensor {self.id}'})
    self.lock = Lock()
    
    # MQTT
    self.client = mqtt.Client(client_id=self.name, callback_api_version=mqtt.CallbackAPIVersion.VERSION2, userdata=None)
    self.topic = f'/sensor/{self.type.lower()}/{self.id}'
    self.client.on_connect = self.on_connect

    # GRPC
    self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    self.channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
    self.stub = grpc_sensor.SensorServerStub(self.channel)
  
  
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
  
  # Read the event queue and publish the events
  def read_event_queue(self):
    while self.is_active:
        event = self.eventsQueue.get_event()
        image= self.capture_event()
        self.publish_event(event, image)
        
  # Simulate motion detection
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
      sensor_value = self.get_sensor_value()
      motion_event = Event(event_type, event_time, sensor_value)
      
      # Add event to queue
      self.eventsQueue.add_event(motion_event)
      self.logger.info(f'MOTION EVENT HAPPENED')
      
  # MQTT METHODS -----------------------------
  
  # Triggered when the sensor connects to the MQTT broker
  def on_connect(self, client, userdata, flags, return_code, properties):
    if return_code == 0:
        self.logger.info(f'Connected to MQTT broker')
    else:
        self.logger.info(f'Failed to connect to MQTT broker', return_code)  
  
  # Publish the event to the MQTT broker
  def publish_event(self, event,image):
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
  
  # ABSTRACT METHODS -----------------------------
  # Each sensor type returns a different value
  @abstractmethod
  def get_sensor_value(self):
      pass

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
  # TODO: Implement the camera capture
  def capture_event(self):
    with self.lock:
        image = os.urandom(4)
        self.logger.info(f'Capture triggered.')
        return image
    


