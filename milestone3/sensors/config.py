
class Config:
  HOSTNAME = "localhost"
  PORT = 1883

  EVENT_TYPE = 'motion'
  DATE_FORMAT = '%Y-%m-%d_%Hh-%Mm-%Ss'
  EVENT_MIN_INTERVAL = 3
  EVENT_MAX_INTERVAL = 10

  # The humidity value in %
  HUMIDITY_MIN_VALUE = 30.0
  HUMIDITY_MAX_VALUE = 90.0
