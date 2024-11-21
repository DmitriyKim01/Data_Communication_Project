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
                    placeholder="Select an option", style={'width' : '100%'}
                )
            , html.Button('Trigger', id='trigger-btn', n_clicks=0),], style={'display': 'flex', 'width': '30%', 'gap':'3rem'}), 

            html.Div([
                html.Button('Enable', id='enable-btn', n_clicks=0,  style={
                'width': '100px',
                'height': '40px',
                'borderRadius': '10px'  
            }),
                html.Button('Disable', id='disable-btn', n_clicks=0,style={
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
# Run the app
if __name__ == "__main__":
    app.run_server(debug=True)
