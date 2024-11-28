# Sensor-Middleware-Computer System

## Overview

This project consists of three primary components (or nodes):

1. **Sensor Node**: A device equipped with a camera and running a gRPC server. Each sensor waits for trigger commands from the middleware and generates random events, which are published via MQTT.
2. **Computer Dashboard Node**: You can use a dashboard which will allow you to choose a specific sensor, trigger capture, listen to one or many nodes.
3. **Middleware**: A gRPC server that handles trigger requests from the computer nodes and provides a list of available sensors. It also manages a dictionary of sensor data and triggers actions.

### Security

We implemented the following assymetric encryption strategy:

1. When starting a new dashboard, the computer will generate a pair of private and public keys, and send public key to a server and sensors
2. Both server and sensors have a dictionary of public keys from diff computers
3. For now, we are encrypting the available ids trigger on the grpc part
4.  We were unable to encrypt the image, since it has very big size 

### Components Breakdown

#### 1. Middleware (`grpc_server.py`)

- **Purpose**: The middleware acts as the bridge between the sensors and the computers. It exposes gRPC methods that allow computers to:
  - **Trigger** a specific sensor.
  - **Get** a list of available sensor IDs.
- **Sensor Dictionary**: The middleware maintains a dictionary of all sensors. This dictionary is populated when a sensor is created, and it maps sensor IDs to their respective IP addresses.

#### 2. Sensor Node

- **Purpose**: Each sensor node runs a gRPC server and listens for trigger requests. When created, it starts generating events at random intervals. These events are published using MQTT to a topic based on the sensor type and ID.
- **Sensor Types**: There are three types of sensors:
  - **Humidity**
  - **Temperature**
  - **Wind**
- **Sensor Architecture**: The sensors are based on an abstract class, and each sensor type inherits from this class. The main difference between sensor types is the data they generate.

#### 3. Dashboard

You can use web dashboard by running:

  ```bash
 python /operating_pc/dashboard.py
  ```

---

## Running the Project

### Step 1: Set up Environment

Before running the system, ensure that each terminal has its environment variables set up. This can be done by activating a virtual environment or setting the required environment variables.

### Step 1.5 Generate proto files

1. Generate proto files

  ```bash
 python /proto/generate_proto.py
  ```

2. Change the import type in sensor_pb2_grpc.py

Instead of (import sensor_pb2 as sensor__pb2) change it to (from proto import sensor_pb2 as sensor__pb2)

### Step 2: Start the Middleware

1. Open a terminal window and navigate to the **server** directory.
2. Start the middleware by running the following command:
   ```bash
   python server/grpc_server.py

### Step 3: Start the Sensors
1. Open a second terminal window and navigate to the sensors directory.
2. Run the runner.py file to start the sensors, their gRPC servers, and MQTT event generation:
    ```bash 
    python sensors/runner.py

### 4: Start the Dashboard 
  ```bash
 python /operating_pc/dashboard.py
  ```


## Project Structure
![Project structure](../screenshots/Project%20Structure.png)
## Dependencies

- **paho-mqtt**: For MQTT communication.
- **grpcio**: For gRPC communication.
- **protobuf**: For defining the data structures.
- **argparse**: For command-line argument parsing.

Install dependencies with:
```bash
pip install -r requirements.txt
