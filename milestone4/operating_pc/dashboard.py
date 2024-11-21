import dash 
from dash import dcc, html, Input, Output, callback
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
messages = [
    "Message 1",
    "Message 2",
    "Message 3",
    "Message 4",
    "Message 5"
]

# Layout
app.layout = html.Div([
    # Container for the entire content, centered on the screen
    html.Div([
        # Top Bar
        html.Div([
            html.Div([
                dcc.Dropdown(
                    id='select-dropdown',
                    options=[
                        {'label': 'Option 1', 'value': 'option1'},
                        {'label': 'Option 2', 'value': 'option2'},
                    ],
                    placeholder="Select an option", style={'width' : '100%'}
                )
            , html.Button('Trigger', id='trigger-btn', n_clicks=1 ),], style={'display': 'flex', 'width': '30%', 'gap':'3rem'}), 

            html.Div([
                html.Button('Enable', id='enable-btn',  style={
                'width': '100px',
                'height': '40px',
                'borderRadius': '10px'  
            }),
                html.Button('Disable', id='disable-btn',style={
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
            html.Div([
                html.H5("MQTT Log"),
                # Placeholder for MQTT Log content
                html.Div(id='mqtt-log', style={'height': '300px', 'border': '1px solid black', 'padding': '10px', 'overflow-y': 'auto'}, children=[
                html.Ul(id='mqtt-log-list')
            ])                
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
            html.Div([
    html.H5("Action Log"),
    html.Ul(id='action-log', style={'height': '300px', 'border': '1px solid black', 'padding': '10px', 'overflow-y': 'auto'})  
], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),  

    # Bottom Bar
     html.Div([
    # Text on top-left
    html.Div([
        html.P(["Sensor Requestor"],style={'margin':'1px','borderBottom' : '1px solid #ccc','width' :'20%'})
    ], style={'width': '100%', 'display': 'block', 'paddingLeft': '20px'}),  

    # Area with the button and ids container
    html.Div([
        html.Button("Get IDs", id='get-ids-btn', n_clicks=0),
        html.Div(id='ids-area', style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '10px'})
    ], style={'width': '100%', 'height': '100%',  'display': 'flex', 'textAlign': 'right', 'paddingRight': '20px'}),
], style={'borderTop': '1px solid #ccc', 'border': '1px solid #ccc', 'padding': '5px', 'display': 'flex', 'flexDirection':'column', 'alignItems': 'flex-start', 'height': '57px', 'gap' :'3px'})

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
    'display' : 'flex',
    'alignItems': 'center', 
    'justifyContent': 'center', 
    'height': '100vh',  
    'margin': 0, 
    'padding': 0,  
}),

action_log = []
# Filter for logging
class ComputerNameFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'computer_name'):
            record.computer_name = 'N/A'
        return True
computer = OperatingComputer(id="0001", trigger=True, listen=True, type="all", sensor="0001")
@app.callback(
    Output('action-log', 'children'),
    Input('trigger-btn', 'n_clicks')  
)
def update_logs(n_clicks):
    if n_clicks > 0:
        print("Clicked")  # Print to the console when button is clicked

        # Append new log entry as a <li> element
        new_log = html.Li(f"Trigger button clicked at {time.ctime()}")  #\
        action_log.append(new_log)  # Add to action log

    return action_log 

if __name__ == '__main__':
  app.run_server(debug=True)