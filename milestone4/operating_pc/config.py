class Config:
  HOSTNAME = "35.183.124.89"
  PORT = 1883
  GRPC_SERVER_ADDRESS = "localhost:50051"
  SENSOR_TYPES = ['All', 'Any', 'Temperature', 'Humidity', 'Wind', '+', 'Image']
  CONNECTION_TIMEOUT = 10