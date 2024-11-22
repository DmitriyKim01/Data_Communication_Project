
from sensor import Sensor
import time
import logging
from config import Config

class SensorNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'sensor_name'):
            record.sensor_name = 'N/A'
        return True

if __name__ == "__main__":
  logging.basicConfig(
      level=logging.INFO,
      format=f'%(levelname)s - [{Config.HOSTNAME}:{Config.PORT}] - (%(sensor_name)s) - %(message)s'
  )
  
  logger = logging.getLogger()
  logger.addFilter(SensorNameFilter())
      
  sensor = Sensor('0001', 3001)
  
  sensors = [sensor]
  
  try:
    for sensor in sensors:
      sensor.start()
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    logger.warning("Keyboard interruption trapped. Shutting down...")
  except Exception as e:
    logger.critical(e)
  finally:
    logger.warning("Please wait for the system to shutdown...")
    for sensor in sensors:
      sensor.stop()
    logger.info("Shutdown complete.")
  
  