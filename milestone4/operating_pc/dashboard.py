# -------------------------- Imports --------------------------
import dash
from dash import dcc, html, Input, Output, callback, State, ctx
import logging
import paho.mqtt.client as mqtt
import argparse
import grpc
import proto.sensor_pb2 as sensor_pb2 
import proto.sensor_pb2_grpc as sensor_pb2_grpc
from config import Config
import time
import json
import base64
from computer import OperatingComputer

# -------------------------- Logging Setup --------------------------
# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

# Custom filter for logging
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True

# -------------------------- Dash App Initialization --------------------------
# Initialize the Dash app
app = dash.Dash(__name__)

# Initialize logs
action_log = []
mqtt_log = []
# -------------------------- Callback Functions --------------------------

# Callback to get sensor IDs and dropdown options
@app.callback(
    [Output('ids-area', 'children'),  
     Output('select-dropdown', 'options')], 
    Input('get-ids-btn', 'n_clicks')  
)
def get_sensor_ids_and_options(n_clicks):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    try:
        # Fetch the sensor IDs
        sensor_ids = computer.get_sensor_ids()
        ids_area_content = [html.Div(f"Sensor ID: {sensor_id}", style={'margin': '5px', 'borderRight' : '2px solid #000000', 'paddingRight': '5px'}) for sensor_id in sensor_ids]
        # Create options for the dropdown
        dropdown_options = [{'label': f'Sensor {sensor_id}', 'value': sensor_id} for sensor_id in sensor_ids]

        return ids_area_content, dropdown_options
    except Exception as e:
        logging.error(f"Failed to fetch sensor IDs: {str(e)}")
        error_message = [html.Div("Failed to fetch sensor IDs.", style={'color': 'red'})]
        return error_message, []  

# Callback to update and clear logs
@app.callback(
    Output('action-log', 'children'),  
    [Input('trigger-btn', 'n_clicks'),  
     Input('clear-action-log-btn', 'n_clicks'), 
     Input('select-dropdown', 'value')  
])
def update_and_clear_logs(trigger_clicks, clear_clicks, selected_option):
    trigger_clicks = trigger_clicks or 0
    clear_clicks = clear_clicks or 0
    # Clear the log if the clear button was clicked
    if ctx.triggered_id == 'clear-action-log-btn':
        action_log.clear()  
        msg = "Action log cleared."
    elif ctx.triggered_id == 'trigger-btn':
        if selected_option:
            new_log = html.Li(f"Trigger button clicked at {time.ctime()}, selected option: {selected_option}")
        else:
            new_log = html.Li(f"Trigger button clicked at {time.ctime()}, no option selected")
        action_log.append(new_log) 
      
        msg = "New log added."

    return action_log  

@app.callback(
    Output('mqtt-log-list', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('clear-mqtt-log-btn', 'n_clicks')] 
)
def update_mqtt_log(n, clear_clicks):
    # Clear MQTT log if the clear button was clicked
    if ctx.triggered_id == 'clear-mqtt-log-btn':
        mqtt_log.clear()

    # Fetch the new log data
    new_log_data = computer.get_log()

    # If new log data is not empty or None, append it to the mqtt_log
    if new_log_data:
        mqtt_log.append(new_log_data)


    if mqtt_log:
        return [html.Li(log) for log in mqtt_log]
    else:
        return []  



app.layout = html.Div([
    # Container for the entire content
    html.Div([
        # Top Bar
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='select-dropdown',
                    options=[],
                    placeholder="Select a sensor",
                ),
                html.Button('Trigger', id='trigger-btn', n_clicks=0),
                html.Button('Enable', id='enable-btn'),
                html.Button('Disable', id='disable-btn'),
            ], className="top-bar-actions"),

            html.Div([
    dcc.Dropdown(
        id='sensor-id-dropdown',
        options=[{'label': 'Any', 'value': 'Any'}],
        placeholder="Select Sensor ID",
        className="dropdown"
    ),
    dcc.Dropdown(
        id='type-dropdown',
        options=[
            {'label': 'Humidity', 'value': 'Humidity'},
            {'label': 'Temperature', 'value': 'Temperature'},
            {'label': 'Wind', 'value': 'Wind'},
            {'label': 'Any', 'value': 'Any'},
            {'label': 'All', 'value': 'All'},
            {'label': 'Images', 'value': 'Images'}
        ],
        placeholder="Select Type",
        className="dropdown"
    ),
    html.Button('Subscribe', id='subscribe-btn', className="subscribe-button")
], id="top-bar-extra"),

        ], className="top-bar"),

        # Middle Area
        html.Div([
            # MQTT Log Section
            html.Div([
                html.Div([
                    html.H5("MQTT Log"),
                    html.Button('Clear Log', id='clear-mqtt-log-btn'),
                ], className="log-header"),

                html.Div([
                    html.Div([
                        dcc.Interval(
                            id='interval-component',
                            interval=1 * 1000,
                            n_intervals=0
                        ),
                        html.Ul(id='mqtt-log-list'),
                    ], className="log-content")
                ]),
            ], className="log-section"),

            # Action Log Section
            html.Div([
                html.Div([
                    html.H5("Action Log"),
                    html.Button('Clear Log', id='clear-action-log-btn'),
                ], className="log-header"),

                html.Ul(id='action-log', className="log-content")
            ], className="log-section"),
        ], className="middle-area"),

        # Bottom Bar
        html.Div([
            html.Div([
                html.P("Sensor Requestor", className="sensor-requestor-header"),
            ], className="sensor-requestor-container"),

            html.Div([
                html.Button("Get IDs", id='get-ids-btn', n_clicks=0),
                html.Div(id='ids-area', className="ids-area"),
            ], className="bottom-bar-actions"),
        ], className="bottom-bar")
    ], className="main-container")
], className="app-container")

# -------------------------- Run the App --------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--id', default='0001', help='Identifies computer')
    parser.add_argument('-t', '--trigger', action='store_true', help='Allows computer to trigger sensors')
    parser.add_argument('-l', '--listen', action='store_true', help='Allows computer to listen to sensors')
    parser.add_argument('-T', '--type', help='Sensor type')
    parser.add_argument('-s', '--sensor', help='Sensor ID')
    parser.add_argument('-a', '--all', action='store_true', help="Returns a list of available ids to trigger.")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format=f'%(levelname)s - [{Config.HOSTNAME}:{Config.PORT}] - (%(computer_name)s) - %(message)s'
    )
    logger = logging.getLogger()
    logger.addFilter(ComputerNameFilter())

    # If -a is used, display available sensor IDs but don't exit
    if args.all:
        computer = OperatingComputer(args.id, False, False, '', '')
        available_ids = computer.get_sensor_ids()
        logger.info(f"Available Sensor Ids are {available_ids}")
    
    # Check if required arguments are passed for normal operation
    if not args.type:
        logger.error('Computer must specify a sensor type ( -T | --type )')
        exit(1)
    if not args.sensor:
        logger.error('Computer must specify a sensor ID ( -s | --sensor )')
        exit(1)
    if not args.trigger and not args.listen:
        logger.error('Computer must specify a trigger flag ( -t | --trigger ) or a listen flag ( -l | --listen )')
        exit(1)

    # Create a new computer instance
    computer = OperatingComputer(args.id, args.trigger, args.listen, args.type, args.sensor)
        
    try:
        computer.listen_to_sensors()
        app.run_server(debug=False, port=1883)
    except KeyboardInterrupt:
        computer.disconnect()
