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
        # Initialize sensors
        self.sensors = {
            '0001': HumiditySensor('0001', 'Humidity'),
            '0002': TemperatureSensor('0002', 'Temperature'),
            '0003': WindSensor('0003', 'Wind')
        }

    def TriggerCapture(self, request, context):
        """Triggered when the client sends a request to capture an image."""
        sensor_id = request.sensor_id
        # Ensure the sensor exists
        if sensor_id not in self.sensors:
            context.set_details(f"Sensor with ID {sensor_id} not found.")
            context.set_code(grpc.StatusCode.NOT_FOUND)
            return sensor_pb2.CaptureResponse()  

        # Get the correct sensor and trigger the image capture
        sensor = self.sensors[sensor_id]
        print("Received A trigger ")
        try:
            image_data = sensor.capture()  
            return sensor_pb2.CaptureResponse(image_data=image_data)
        except Exception as e:
            context.set_details(f"Error capturing image: {e}")
            context.set_code(grpc.StatusCode.INTERNAL)
            return sensor_pb2.CaptureResponse()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_sensor.add_SensorServiceServicer_to_server(SensorServiceServicer(), server)
    server.add_insecure_port('[::]:50051')  
    print("Server started, listening on port 50051...")
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
