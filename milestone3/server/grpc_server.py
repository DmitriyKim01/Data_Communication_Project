# server/grpc_server.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sensors.grpc_sensor import serve

if __name__ == '__main__':
    serve()
