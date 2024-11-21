import grpc as grpc
from concurrent import futures
import proto.sensor_pb2 as sensor_pb2
import proto.sensor_pb2_grpc as grpc_sensor

    
class SensorServiceServicer(grpc_sensor.SensorServerServicer):
    def __init__(self):
        self.sensors = {}
    
    # Capture an image from a sensor
    def TriggerCapturePc(self, request, context):
        try:
            current_sensor_ip = self.sensors[request.id]
            channel = grpc.insecure_channel(current_sensor_ip)  
            stub = grpc_sensor.SingleSensorStub(channel)
            trigger_request = sensor_pb2.TriggerRequest(id=request.id)
            response = stub.TriggerCapture(trigger_request)
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
        sensor_ids = list(self.sensors.keys())  
        return sensor_pb2.AvailableSensors(ids=sensor_ids)
    
def serve():
    # Create the server and add the servicer
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    grpc_sensor.add_SensorServerServicer_to_server(SensorServiceServicer(), server)

    # Bind the server to a port
    server.add_insecure_port('[::]:50051')  
    print("Server started, listening on port 50051...")

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
