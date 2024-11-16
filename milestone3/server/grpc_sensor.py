import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import grpc as grpc
import server.config as Config
from concurrent import futures
import proto.sensor_pb2 as sensor_pb2
import proto.sensor_pb2_grpc as grpc_sensor

    
class SensorServiceServicer(grpc_sensor.SensorServerServicer):
    
    def __init__(self):
        pass
        
    def TriggerCapturePc(self, request, context):
        # Establish connection with the sensor server
        try:
            # Create the gRPC channel to the sensor server
          
            channel = grpc.insecure_channel("localhost:3001")  
            stub = grpc_sensor.SingleSensorStub(channel)
            trigger_request = sensor_pb2.TriggerRequest(id=request.id)
            response = stub.TriggerCapture(trigger_request)
            return response

        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error during gRPC call: {e}")
            return sensor_pb2.CaptureResponse()
        
    def AddSensor(self, request, context):
        id = request.id
        ip = request.ip
        port = request.port
        print (f'{id}, {ip}, {port}')
        return sensor_pb2.EmptyResponse()
def serve():
    # Create the server and add the servicer
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_sensor.add_SensorServerServicer_to_server(SensorServiceServicer(), server)

    # Bind the server to a port
    server.add_insecure_port('[::]:50051')  
    print("Server started, listening on port 50051...")

    # Start the server
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
