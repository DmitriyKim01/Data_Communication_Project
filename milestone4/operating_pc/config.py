class Config:
  HOSTNAME = "192.168.0.145"
  PORT = 1883
  GRPC_SERVER_ADDRESS = "localhost:7070"
  SENSOR_TYPES = ['All', 'Any', 'Temperature', 'Humidity', 'Wind', '+', 'Images']
  CONNECTION_TIMEOUT = 10