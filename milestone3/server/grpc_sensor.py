import grpc
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from concurrent import futures
import proto.sensor_pb2 as sensor_pb2
import proto.sensor_pb2_grpc as grpc_sensor
from sensors.humidity import HumiditySensor
from sensors.temperature import TemperatureSensor
from sensors.wind import WindSensor

class SensorServiceServicer(grpc_sensor.SensorServiceServicer):
    
    def __init__(self):
        pass

 
    def TriggerCapture(self, request, context):
        """Triggered when the client sends a request to capture an image."""
        
        
    def GetSensorIds(self, request, context):
        """Returns a list of all sensor IDs."""
        sensor_ids = list(self.sensors.keys())
        return sensor_pb2.SensorIdsResponse(ids=sensor_ids)
    
    def EventCaptures(self):
        for sensor in self.sensors.values(): 
            try:
                sensor.start() 
            except Exception as e:
                print(f"Error starting senso")

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_sensor.add_SensorServiceServicer_to_server(SensorServiceServicer(), server)
    server.add_insecure_port('[::]:50051')  
    print("Server started, listening on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
