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
import logging

# Set up logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')


# Initialize the Dash app
app = dash.Dash(__name__)

action_log = []
# Filter for logging
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True
computer = OperatingComputer(id="0001", trigger=True, listen=True, type="all", sensor="0001")

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
        ids_area_content = [html.Div(f"Sensor ID: {sensor_id}", style={'margin': '5px'}) for sensor_id in sensor_ids]
        # Create options for the dropdown
        dropdown_options = [{'label': f'Sensor {sensor_id}', 'value': sensor_id} for sensor_id in sensor_ids]

        return ids_area_content, dropdown_options
    except Exception as e:
        logging.error(f"Failed to fetch sensor IDs: {str(e)}")
        error_message = [html.Div("Failed to fetch sensor IDs.", style={'color': 'red'})]
        return error_message, []  
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


# Layout --------------------------------------------------------------------------------------------------------
app.layout = html.Div([
    # Container for the entire content, centered on the screen
    html.Div([
        # Top Bar
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='select-dropdown',
                    options=[], 
                    placeholder="Select a sensor",
                    style={'width': '100%'}
                ),
                html.Button('Trigger', id='trigger-btn', n_clicks=0),
            ], style={'display': 'flex', 'width': '30%', 'gap': '3rem'}),

            html.Div([
                html.Button('Enable', id='enable-btn', style={
                    'width': '100px',
                    'height': '40px',
                    'borderRadius': '10px'
                }),
                html.Button('Disable', id='disable-btn', style={
                    'width': '100px',
                    'height': '40px',
                    'borderRadius': '10px'
                }),
            ], style={
                'display': 'flex',
                'float': 'right',
                'textAlign': 'right',
                'width': '80%',
                'height': '100%',
                'justifyContent': 'center',
                'gap': '20px'
            })
        ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px', 'borderBottom': '1px solid #ccc'}),

        # Middle Area (Two big boxes, horizontally next to each other)
html.Div([
    # MQTT Log Section
    html.Div([
        # Header for MQTT Log with button
        html.Div([
            html.H5("MQTT Log", style={'margin': 0}),
            html.Button('Clear Log', id='clear-mqtt-log-btn', style={
                'marginLeft': '10px', 
                'height': '30px',
                'alignSelf': 'center'
            }),
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}), 

        # Placeholder for MQTT Log content
        html.Div(id='mqtt-log', style={
            'height': '300px', 
            'border': '1px solid black', 
            'padding': '10px', 
            'overflowY': 'auto',
            'marginTop' : '15px'

        }, children=[
            html.Ul(id='mqtt-log-list')
        ])
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

    # Action Log Section
    html.Div([
        html.Div([
            html.H5("Action Log", style={'margin': 0}),
            html.Button('Clear Log', id='clear-action-log-btn' , style={
                'marginLeft': '10px',  
                'height': '30px',
                'alignSelf': 'center'
            }),
        ], style={'display': 'flex', 'alignItems': 'center', 'gap': '10px'}), 

        html.Ul(id='action-log', style={
            'height': '300px', 
            'border': '1px solid black', 
            'padding': '10px', 
            'overflowY': 'auto',
            'marginTop' : '15px'
        })
    ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),


        # Bottom Bar
        html.Div([
            # Text on top-left
            html.Div([
                html.P(["Sensor Requestor"], style={'margin': '1px', 'borderBottom': '1px solid #ccc', 'width': '20%'})
            ], style={'width': '100%', 'display': 'block', 'padding': '8px'}),

            # Area with the button and ids container
            html.Div([
                html.Button("Get IDs", id='get-ids-btn', n_clicks=0),
                html.Div(id='ids-area', style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '10px'})
            ], style={'width': '100%', 'height': '50px', 'display': 'flex', 'textAlign': 'right', 'paddingRight': '20px'}),
        ], style={'borderTop': '1px solid #ccc', 'border': '1px solid #ccc', 'padding': '5px', 'display': 'flex', 'flexDirection': 'column', 'alignItems': 'flex-start', 'height': '100%', 'gap': '3px'})
    ], style={
        'width': '70%',  
        'maxWidth': '1200px',  
        'margin': '0 auto', 
        'boxSizing': 'border-box',  
        'padding': '20px',  
        'border': '1px solid #000000',  
        'borderRadius': '8px',
    })
], style={
    'display': 'flex',
    'alignItems': 'center',
    'justifyContent': 'center',
    'height': '100vh',  
    'margin': 0, 
    'padding': 0,  
})

if __name__ == '__main__':
  app.run_server(debug=True)