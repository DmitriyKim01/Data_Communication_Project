
class Config:
  HOSTNAME = "localhost"
  PORT = 1883

  EVENT_TYPE = 'motion'
  DATE_FORMAT = '%Y-%m-%d_%Hh-%Mm-%Ss'
  EVENT_MIN_INTERVAL = 5
  EVENT_MAX_INTERVAL = 10

  # The humidity value in %
  HUMIDITY_MIN_VALUE = 30.0
  HUMIDITY_MAX_VALUE = 90.0
  
  # The wind measured in km/h
  WIND_MIN_VALUE = 0.0
  WIND_MAX_VALUE = 100.0
  
  # The temperature measured in Celsius
  TEMPERATURE_MIN_VALUE = -50.0
  TEMPERATURE_MAX_VALUE = 50.0
