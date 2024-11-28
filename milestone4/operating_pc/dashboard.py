# -------------------------- Imports --------------------------

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import dash
from dash import dcc, html, Input, Output, callback, State, ctx
import logging
import paho.mqtt.client as mqtt
from config import Config
import time
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
     Output('select-dropdown', 'options'),
     Output('sensor-id-dropdown', 'options')], 
    Input('get-ids-btn', 'n_clicks')  
)
def get_sensor_ids_and_options(n_clicks):
    if n_clicks == 0:
        raise dash.exceptions.PreventUpdate

    try:
        # Fetch the sensor IDs
        sensor_ids = computer.get_sensor_ids()
        ids_area_content = [
            html.Div(f"Sensor ID: {sensor_id}", 
                     style={'margin': '5px', 'borderRight': '2px solid #000000', 'paddingRight': '5px'})
            for sensor_id in sensor_ids
        ]
        
        # Create options for the select-dropdown and sensor-id-dropdown
        dropdown_options = [{'label': f'Sensor {sensor_id}', 'value': sensor_id} for sensor_id in sensor_ids]
        sensor_id_options = [{'label': 'Any', 'value': 'Any'}] + dropdown_options  # Include "Any" option

        return ids_area_content, dropdown_options, sensor_id_options
    except Exception as e:
        logging.error(f"Failed to fetch sensor IDs: {str(e)}")
        error_message = [html.Div("Failed to fetch sensor IDs.", style={'color': 'red'})]
        return error_message, [], []

@app.callback(
    Output('action-log', 'children'),  
    [Input('trigger-btn', 'n_clicks'),  
     Input('clear-action-log-btn', 'n_clicks'),
     Input('subscribe-btn', 'n_clicks'),
     Input('enable-btn', 'n_clicks'),
     Input('disable-btn', 'n_clicks')],  
    [State('select-dropdown', 'value'),  
     State('type-dropdown', 'value'),  
     State('sensor-id-dropdown', 'value')]  
)
def manage_action_log(trigger_clicks, clear_clicks, subscribe_clicks, enable_clicks, disable_clicks, selected_option, sensor_type, sensor_id):
    global action_log  # Ensure we use the global action log list
    trigger_clicks = trigger_clicks or 0
    clear_clicks = clear_clicks or 0
    subscribe_clicks = subscribe_clicks or 0
    enable_clicks = enable_clicks or 0
    disable_clicks = disable_clicks or 0

    # Determine the triggering input
    triggered_id = ctx.triggered_id

    if triggered_id == 'clear-action-log-btn':
        # Clear the action log
        action_log.clear()
        action_log.append(html.Li("Action log cleared.", style={'color': 'blue'}))

    elif triggered_id == 'trigger-btn':
        # Handle trigger button logic
        if selected_option:
            computer.trigger_capture(selected_option)
            new_log = html.Li(
                f"Trigger button clicked at {time.ctime()}, selected option: {selected_option}",
                style={"color": "orange"}
            )
        else:
            new_log = html.Li(
                "no option selected",
                style={"color": "red"}
            )
        action_log.append(new_log)

    elif triggered_id == 'subscribe-btn':
        if sensor_id == "Any":
            sensor_id = "+"
        # Handle subscription logic
        if not sensor_type or not sensor_id:
            action_log.append(html.Li("Please select both sensor type and sensor ID.", style={'color': 'red'}))
        else:
            try:
                success = computer.listen_to_sensors(sensor_type.lower(), sensor_id.lower())
                if success:
                    action_log.append(html.Li(f"Successfully subscribed to /sensor/{sensor_type.lower()}/{sensor_id.lower()}", style={'color': 'green'}))
                else:
                    action_log.append(html.Li(f"Failed to subscribe to /sensor/{sensor_type.lower()}/{sensor_id.lower()}", style={'color': 'red'}))
            except Exception as e:
                logging.error(f"Subscription failed: {str(e)}")
                action_log.append(html.Li(f"Error during subscription: {str(e)}", style={'color': 'red'}))
                
    #Handling enable/disable logic
     # Enable button logic (add your own logic here)
    elif triggered_id == 'enable-btn':
        action_log.append(html.Li(f"Enable button clicked at {time.ctime()}", style={'color': 'green'}))
        computer.enable_sensor(sensor_id=sensor_id)

    # Disable button logic (add your own logic here)
    elif triggered_id == 'disable-btn':
        action_log.append(html.Li(f"Disable button clicked at {time.ctime()}", style={'color': 'red'}))
        computer.disable_sensor(sensor_id=sensor_id)

    # Return the updated action log
    return action_log



@app.callback(
    Output('mqtt-log-list', 'children'),
    [Input('interval-component', 'n_intervals'),
     Input('clear-mqtt-log-btn', 'n_clicks')]
)
def update_mqtt_log(n_intervals, clear_clicks):
    global mqtt_log

    # Determine what triggered the callback
    if ctx.triggered_id == 'clear-mqtt-log-btn':
        # Clear MQTT log
        mqtt_log.clear()
        computer.clear_log()
        return []  

    # Fetch the new log data
    new_log = computer.get_log()

    # Check for differences in the log and update if needed
    if new_log != mqtt_log:
        mqtt_log = new_log

    # Return the updated log list
    if mqtt_log:
        return [html.Li(log_entry) for log_entry in mqtt_log]
    else:
        return []  



app.layout = html.Div([
    # Container for the entire content
    html.Div([
       #Header Bar
        html.Div([
            html.Div("GRPC", className="header-item"),
                html.Div([], className="vertical-divider"),

            html.Div("MQTT", className="header-item"),
        ], className="header-bar"),
    # Top Bar
html.Div([
    # Left Section
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

    # Divider
    html.Div([], className="vertical-divider"),

    # Right Section
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
    ], id="top-bar-extra")
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
                html.Div([], className="vertical-divider"),
                html.Div(id='ids-area', className="ids-area"),
            ], className="bottom-bar-actions"),
        ], className="bottom-bar")
    ], className="main-container")
], className="app-container")

# -------------------------- Run the App --------------------------
if __name__ == '__main__':
    # Create a new computer instance
    computer = OperatingComputer("0001", True, False, "all", "0001")
    computer.send_public_key_to_server()
    try:
        app.run_server(debug=False, port=50129)
    except KeyboardInterrupt:
        computer.disconnect()
