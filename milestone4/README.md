# Sensor-Middleware-Computer System

## Overview

This project consists of three primary components (or nodes):

1. **Sensor Node**: A device equipped with a camera and running a gRPC server. Each sensor waits for trigger commands from the middleware and generates random events, which are published via MQTT.
2. **Computer Node**: A device that can either trigger a sensor, listen to sensor events, or do both. It communicates with the middleware and interacts with the sensors based on the configured role.
3. **Middleware**: A gRPC server that handles trigger requests from the computer nodes and provides a list of available sensors. It also manages a dictionary of sensor data and triggers actions.

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

#### 3. Computer Node

- **Purpose**: The computer node can serve three roles:
  - **Trigger Computer**: Sends a trigger request to the middleware to activate a specific sensor.
  - **Listen Computer**: Listens to MQTT topics based on sensor data.
  - **Trigger and Listen Computer**: Both triggers and listens to sensors.

### Command-Line Arguments for Computers

The computer can be configured with various command-line arguments to define its behavior:

- **`-i, --id`**: Identifies the computer (default: `0001`).
- **`-t, --trigger`**: Enables the computer to trigger sensors.
- **`-l, --listen`**: Enables the computer to listen to sensors.
- **`-T, --Type`**: Specifies the sensor type (e.g., `temperature`, `humidity`, `wind`).
- **`-s, --sensor`**: Specifies the sensor ID.
- **`-a, --all`**: Lists all available sensor IDs from the middleware.

### Computer Use Cases

1. **Trigger Computer**: Triggers a sensor via the middleware.
   - **Run Command**: `python computer.py -t -T "type" -s "sensor id"`

2. **Listen Computer**: Listens to MQTT topics based on the specified sensor.
   - **Run Command**: `python computer.py -l -T "type" -s "sensor id"`

3. **Both Trigger and Listen Computer**: Performs both trigger and listen actions.
   - **Run Command**: `python computer.py -t -l -T "type" -s "sensor id"`

4. **List Available Sensors**: Displays a list of all available sensor IDs.
   - **Run Command**: `python computer.py -a`

---

## Running the Project

### Step 1: Set up Environment

Before running the system, ensure that each terminal has its environment variables set up. This can be done by activating a virtual environment or setting the required environment variables.

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

### 4: Start the Computer
1. Open a third terminal window to run the computer, which can either trigger or listen to sensors, or perform both actions.
2. Trigger a specific sensor:
  ```bash
python computer.py -t -T "sensor type" -s "sensor id"
  ```
3. Listen to a specific sensor:
  ```bash
python computer.py -l -T "sensor type" -s "sensor id"
  ```
4. Trigger and listen to sensors:
  ```bash
python computer.py -t -l -T "sensor type" -s "sensor id"
  ```
5. List all available sensors:
  ```bash
python computer.py -a
  ```
### Example Workflow
1. Start Middleware:
 ```bash
python server/grpc_server.py
  ```

2. Start Sensors:
 ```bash
python sensors/runner.py
  ```

3. Trigger a Sensor:
 ```bash
python computer.py -t -T "humidity" -s "sensor_01"
  ```

4. Listen to Sensor Events:
 ```bash
python computer.py -l -T "temperature" -s "sensor_02"
  ```

5. Trigger and Listen:
 ```bash
python computer.py -t -l -T "wind" -s "sensor_03"
  ```

---
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
