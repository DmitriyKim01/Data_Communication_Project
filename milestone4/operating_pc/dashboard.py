import dash
from dash import dcc, html

# Initialize the Dash app
app = dash.Dash(__name__)

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
                    placeholder="Select an option",
                )
            ], style={'display': 'inline-block', 'width': '20%'}), 

            html.Div([
                html.Button('Trigger', id='trigger-btn', n_clicks=0),
                html.Button('Enable', id='enable-btn', n_clicks=0),
                html.Button('Disable', id='disable-btn', n_clicks=0),
            ], style={'display': 'inline-block', 'float': 'right', 'textAlign': 'right', 'width': '80%'}) 
        ], style={'display': 'flex', 'alignItems': 'center', 'padding': '10px', 'borderBottom': '1px solid #ccc'}),

        # Middle Area (Two big boxes, horizontally next to each other)
        html.Div([
            html.Div([
                html.H5("MQTT Log"),
                # Placeholder for MQTT Log content
                html.Div(id='mqtt-log', style={'height': '300px', 'border': '1px solid black', 'padding': '10px'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}),

            html.Div([
                html.H5("Action Log"),
                # Placeholder for Action Log content
                html.Div(id='action-log', style={'height': '300px', 'border': '1px solid black', 'padding': '10px'})
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '10px'}), 
        ], style={'display': 'flex', 'justifyContent': 'space-between', 'padding': '10px'}),  

        # Bottom Bar
        html.Div([
            html.Div([
                html.Button("Get IDs", id='get-ids-btn', n_clicks=0)
            ], style={'width': '20%', 'display': 'inline-block', 'border': '1px solid #ccc', 'padding': '5px'}),  

            html.Div([
                html.Div(id='ids-area', style={'display': 'flex', 'flexWrap': 'wrap', 'padding': '10px'})
            ], style={'width': '80%', 'display': 'inline-block', 'textAlign': 'right'}),
        ], style={'padding': '10px', 'borderTop': '1px solid #ccc'})
    ], style={
        'width': '80%',  
        'maxWidth': '1200px',  
        'margin': '0 auto', 
        'boxSizing': 'border-box',  
        'padding': '20px',  
        'border': '1px solid #ccc',  
        'borderRadius': '8px'  
    })
])

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
