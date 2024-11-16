import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sensors.config import Config
from threading import Thread
from event_queue import EventQueue
import argparse
import random
import time
import logging
from sensor import Sensor

class TemperatureSensor(Sensor):
  def get_sensor_value(self):
    return random.uniform(Config.TEMPERATURE_MIN_VALUE, Config.TEMPERATURE_MAX_VALUE)

      
    
        
