import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import grpc as grpc
import json
from concurrent import futures
from proto import sensor_pb2
from proto import sensor_pb2_grpc as grpc_sensor
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
    
class SensorServiceServicer(grpc_sensor.SensorServerServicer):
    def __init__(self):
        self.sensors = {}
        self.computers = {}
        self.sensor_states = {}
    # Capture an image from a sensor
    def TriggerCapturePc(self, request, context):
        try:
            print(f'Capture was triggered by PC for sensor {request.sensor_id}')
            current_sensor_ip = self.sensors[request.sensor_id]
            channel = grpc.insecure_channel(current_sensor_ip)  
            stub = grpc_sensor.SingleSensorStub(channel)
            response = stub.TriggerCapture(request)
            print('Capture response:', response)
            return response
        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error during gRPC call: {e}")
            return sensor_pb2.CaptureResponse()
    
    # Add a sensor to the server dictionary
    def AddSensor(self, request, context):
        print(f"Adding sensor {request.id} with address {request.ip}:{request.port}")
        self.sensors[request.id] = f"{request.ip}:{request.port}"
        return sensor_pb2.EmptyResponse()        
    
    # Return the available sensor ids
    def GetSensorIds(self, request, context):
        if self.computers.get(request.id) is None:
            context.set_code(grpc.StatusCode.UNAUTHENTICATED)
            return sensor_pb2.AvailableSensors(ids=[])
        public_key = self.computers[request.id]
        sensor_ids = list(self.sensors.keys())  
        sensor_ids_json = json.dumps(sensor_ids).encode('utf-8')
        try:
            encrypted_sensor_ids = public_key.encrypt(
                sensor_ids_json,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )
            return sensor_pb2.AvailableSensors(ids=encrypted_sensor_ids)
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error encrypting sensor IDs: {e}")
            return sensor_pb2.AvailableSensors(ids=[])
    
    def SendPublicKeyToServer(self, request, context):
        try:
            print(f"Received public key from sensor {request.sensor_id}: {request.public_key}")
            self.computers[request.id] = serialization.load_pem_public_key(request.public_key)
            current_sensor_ip = self.sensors[request.sensor_id]
            channel = grpc.insecure_channel(current_sensor_ip)
            stub = grpc_sensor.SingleSensorStub(channel)
            response = stub.SendPublicKeyToSensor(request)
            print('Public key sent to sensor:', response.message)
            return response
        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error during gRPC call: {e}")
            return sensor_pb2.PublicKeyResponse
        
    def EnableSensor(self, request, context):
        sensor_id = request.sensor_id
        if sensor_id in self.sensors:
            self.sensor_states[sensor_id] = "enabled"
            return sensor_pb2.EnableSensorResponse(status="Sensor enabled")
        
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Sensor {sensor_id} not found.")
            return sensor_pb2.EnableSensorResponse(status="Sensor not found")
        
    def DisableSensor(self, request, context):
        sensor_id = request.sensor_id
        if sensor_id in self.sensors:
            self.sensor_states[sensor_id] = "disabled"
            return sensor_pb2.DisableSensorResponse(status="Sensor disabled")
        else:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Sensor {sensor_id} not found.")
            return sensor_pb2.DisableSensorResponse(status="Sensor not found")
        
def serve():
    # Create the server and add the servicer
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_sensor.add_SensorServerServicer_to_server(SensorServiceServicer(), server)

    # Bind the server to a port
    server.add_insecure_port('[::]:7070')  
    print("Server started, listening on port 7070...")

    # Start the server
    server.start()
    return server

if __name__ == '__main__':
    try:
        server = serve()
        server.wait_for_termination()
    except KeyboardInterrupt:
        print("Server is shutting down. Please wait...")
        server.stop(grace=5).wait()
        print("Server has been shut down.")
