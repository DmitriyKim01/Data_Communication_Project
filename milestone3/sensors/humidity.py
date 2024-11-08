from config import Config
from threading import Thread
from event_queue import EventQueue
import argparse
import random
import time
import logging
from sensor import Sensor

class HumiditySensor(Sensor):
  def get_sensor_value(self):
    return random.uniform(Config.HUMIDITY_MIN_VALUE, Config.HUMIDITY_MAX_VALUE)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', default="0001")
  parser.add_argument('-t', '--test', action='store_true')
  args = parser.parse_args()
  
  if not args.id:
    raise Exception('Missing sensor id')
  
  type = 'Humidity'
  # Configure logging
  logging.basicConfig(
      level=logging.DEBUG,
      format=f'%(levelname)s - ({type} {args.id}) - [{Config.HOSTNAME}:{Config.PORT}] - %(message)s'
  )
  
  humidity_sensor = HumiditySensor(args.id, type)
  
  if args.test:
    try:
      humidity_sensor.start()
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      logging.warning("Keyboard interruption trapped. Shutting down...")
    except Exception as e:
      logging.critical(e)
    finally:
      logging.warning("Please wait for the system to shutdown...")
      humidity_sensor.stop()
      logging.info("Shutdown complete.")

      
    
        
