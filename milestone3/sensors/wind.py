from config import Config
from threading import Thread
from event_queue import EventQueue
import argparse
import random
import time
import logging
from sensor import Sensor

class WindSensor(Sensor):
  def get_sensor_value(self):
    return random.uniform(Config.WIND_MIN_VALUE, Config.WIND_MAX_VALUE)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('-i', '--id', default="0001")
  parser.add_argument('-t', '--test', action='store_true')
  args = parser.parse_args()
  
  if not args.id or not isinstance(args.id, str):
    raise Exception('Missing sensor id')
  
  type = 'Wind'
  # Configure logging
  logging.basicConfig(
      level=logging.DEBUG,
      format=f'%(levelname)s - ({type} {args.id}) - [{Config.HOSTNAME}:{Config.PORT}] - %(message)s'
  )
  
  events_queue = EventQueue()
  humidity_sensor = WindSensor(args.id, type, events_queue)
  
  # Threads
  motion_simulation_thread = Thread(target=humidity_sensor.simulate_motion)
  read_event_queue_thread = Thread(target=humidity_sensor.read_event_queue)
  
  if args.test:
    try:
      motion_simulation_thread.start()
      read_event_queue_thread.start()
      while True:
        time.sleep(1)
    except KeyboardInterrupt:
      logging.warning("Keyboard interruption trapped. Shutting down...")
    except Exception as e:
      logging.critical(e)
    finally:
      logging.warning("Please wait for the system to shutdown...")
      humidity_sensor.stop()
      motion_simulation_thread.join(timeout=1)
      read_event_queue_thread.join(timeout=1)
      time.sleep(1)
      logging.info("Shutdown complete.")

      
    
        
