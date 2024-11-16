import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import grpc as grpc
from grpc import ServerInterceptor
import server.config as Config
from concurrent import futures
import proto.sensor_pb2 as sensor_pb2
import proto.sensor_pb2_grpc as grpc_sensor

class IPLoggingInterceptor(ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        # Extract the client address (usually in the format of 'IP:PORT')
        client_address = handler_call_details.invocation_metadata
        print(f"Client connected from IP: {client_address}")
        return continuation(handler_call_details)
    
class SensorServiceServicer(grpc_sensor.SensorServiceServicer):
    
    def __init__(self):
        pass
        
    def TriggerCapture(self, request, context):
        # Establish connection with the sensor server
        try:
            # Create the gRPC channel to the sensor server
            port = 50000 + int(request.sensor_id)
            channel = grpc.insecure_channel(Config.GRPC_SERVER_ADDRESS)  
            stub = grpc_sensor.SingleSensorStub(channel)
            trigger_request = sensor_pb2.TriggerRequest(sensor_id=request.sensor_id)
            response = stub.TriggerCapture(trigger_request)
            return response

        except grpc.RpcError as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Error during gRPC call: {e}")
            return sensor_pb2.CaptureResponse()

def serve():
    # Create the server and add the servicer
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), interceptors=[IPLoggingInterceptor()])
    grpc_sensor.add_SensorServiceServicer_to_server(SensorServiceServicer(), server)

    # Bind the server to a port
    server.add_insecure_port('[::]:50051')  
    print("Server started, listening on port 50051...")

    # Start the server
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
