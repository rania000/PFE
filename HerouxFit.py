import base64
import csv
from datetime import datetime, timezone
from sre_parse import State
from tkinter.tix import InputOnly
from cv2 import _OUTPUT_ARRAY_DEPTH_MASK_16F
import dash
from dash import dcc, html
import plotly.express as px
import numpy as np
import folium
import pandas as pd
import dash_bootstrap_components as dbc
from TraitCsv import *
import io

data = pd.read_csv("CoursePied.csv")

# dash.plotly -> compo -> upload 
############

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def parse_contents(contents, filename):
    content_type, content_string = contents.split(',')

    decoded = base64.b64decode(content_string)
    try:
        if 'csv' in filename:
            # Assume that the user uploaded a CSV file
            df = pd.read_csv(io.StringIO(decoded.decode('utf-8')))
        elif 'xls' in filename:
            # Assume that the user uploaded an Excel file
            df = pd.read_excel(io.BytesIO(decoded))
    except Exception as e:
        print(e)
        return html.Div([
            'There was an error processing this file.'
        ])
    global data
    data = df
    print(data.head())
    return html.Div([
        html.H5(filename),
        dash.dash_table.DataTable(
            data=df.to_dict('records'),
            columns=[{'name': i, 'id': i} for i in df.columns]
        ),
    ])

def seconds_to_hms(seconds):
    """Convert seconds to hours, minutes, seconds."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def plot_route_on_map(data):
    m = folium.Map(location=[49.47302, 1.06102], zoom_start=11)  # Create a folium map

    coordinates = []  # List to store coordinates for Polyline

    for _, row in data.iterrows():
        lat, lon = float(row["latitude"]), float(row["longitude"])
        coordinates.append([lat, lon])

    # Add a Polyline connecting all points
    folium.PolyLine(coordinates, color="blue").add_to(m)

    m.save("assets/map_with_route.html")  # Save the map to an HTML file

def plot_data_over_time(data):
    times = pd.to_datetime(data["temps"], format="%Y-%m-%d %H:%M:%S%z")
    heart_rates = data["freqCard"].astype(float).fillna(0)
    temperatures = data["temperature"].astype(float).fillna(0)
    elevations = data["elevation"].astype(float).fillna(0)
    vitesseInst = data["vitesseInst"].astype(float).fillna(0)
    # Create interactive plots using Plotly Express
    fig_hr = px.line(
        x=times,
        y=heart_rates,
        labels={"x": "temps", "y": "fréquence cardiaque (bpm)"},
        title="fréquence Cardiaque",
    )
   
    fig_temp = px.line(
        x=times,
        y=temperatures,
        labels={"x": "temps", "y": "Temperature (°C)"},
        title="Temperature",
    )
    fig_elevation = px.line(
        x=times,
        y=elevations,
        labels={"x": "temps", "y": "Elevation (m)"},
        title="Elevation",
    )
    fig_vitesse = px.line(
        x=times,
        y=vitesseInst,
        labels={"x": "temps", "y": "vitesse (m/s)"},
        title="vitesse",
    )

    return fig_hr, fig_temp, fig_elevation, fig_vitesse

def generate_layout(fig_hr, fig_temp, fig_elevation, fig_vitesse):
    return html.Div([
        html.Div(className='header', children=[
            html.H1("FitApp")
        ]),
        html.Div([
    dcc.Upload(
        id='upload-data',
        children=html.Div([
            html.A('Glissez-Selectionnez un fichier')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
        # Allow only one file to be uploaded
        multiple=False
    ),
]),
            html.Div(className='container', children=[
            html.Div(className='section', children=[
                html.Div(className='graph-container graph-container-1', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=fig_hr, id='graph-1'), width=6),
                        dbc.Col(dcc.Graph(figure=fig_temp, id='graph-2'), width=6),
                    ]),
                ])
            ]),
            html.Div(className='section', children=[
                html.Div(className='graph-container graph-container-2', children=[
                    dbc.Row([
                        dbc.Col(dcc.Graph(figure=fig_elevation, id='graph-3'), width=6),
                        dbc.Col(dcc.Graph(figure=fig_vitesse, id='graph-4'), width=6),
                    ]),
                ])
                ]),
            ]),
             html.Div(className='output-container', id='map-container'),
            html.Div(className='output-container', id='output-container-totalDist'),
            html.Div(className='output-container', id='output-container-totalTime'),
            html.Div(className='output-container', id='output-container-freqMoyenne'),
            html.Div(className='output-container', id='output-container-vitesseMoy'),
            html.Div(className='output-container', id='output-container-CO2'),
            html.Div(className='output-container', id='output-container-caloVelo'),
            html.Div(className='slider-container', children=[
                html.Div(className='slider-label', children=[
                    
                    dcc.Slider(
                        id='age-slider',
                        min=10,
                        max=100,
                        step=1,
                        value=48,
                        marks={10: '10', 100: '100'},
                        tooltip={'placement': 'bottom'}
                    ),
                    html.Div(id='age-output-container')
                ]),
                html.Div(className='slider-label', children=[
                    
                    dcc.Slider(
                        id='weight-slider',
                        min=30,
                        max=200,
                        step=1,
                        value=70,
                        marks={30: '30', 200: '200'},
                        tooltip={'placement': 'bottom'}
                    ),
                    html.Div(id='weight-output-container')
                ]),
            ]),
        
        dcc.Store(id='data', data=data.to_dict('records'))

    ])


@app.callback( 
    [dash.dependencies.Output('output-container-totalDist', 'children'),
     dash.dependencies.Output('output-container-totalTime', 'children'),
     dash.dependencies.Output('map-container', 'children'),
     dash.dependencies.Output('graph-1', 'figure'),
    dash.dependencies.Output('graph-2', 'figure'),
    dash.dependencies.Output('graph-3', 'figure'),
    dash.dependencies.Output('graph-4', 'figure'),
     dash.dependencies.Output('data', 'data')],
    [dash.dependencies.Input('upload-data', 'contents')],
    [dash.dependencies.State('upload-data', 'filename')]
)
def update_output(contents, filename):
    if contents is not None:
        children = parse_contents(contents, filename)
    df = data
    
    fig_hr, fig_temp, fig_elevation, fig_vitesse = plot_data_over_time(df)
    return [update_total_distance(df),
            update_total_time(df), 
            update_map(df),
            fig_hr,
            fig_temp,
            fig_elevation,
            fig_vitesse,
            df.to_dict('records')]


    
@app.callback(
    dash.dependencies.Output('age-output-container', 'children'),
    [dash.dependencies.Input('age-slider', 'value')]
)
def update_age_output(age):
    return f'Age: {age} ans'

@app.callback(
    dash.dependencies.Output('weight-output-container', 'children'),
    [dash.dependencies.Input('weight-slider', 'value')]
)
def update_weight_output(weight):
    return f'poids: {weight} kg'

def update_total_distance(data):
    df = pd.DataFrame(data)
    return f"Distance parcouru: {totalDist(df)} km"


def update_total_time(data):
    df = pd.DataFrame(data)
    return f"Durée: {seconds_to_hms(totalTime(df))}"

@app.callback(
    dash.dependencies.Output('output-container-freqMoyenne', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_average_frequency(data):
    df = pd.DataFrame(data)
    return f"Plage de fréquence(en bpm) en fonction de la durée: {calculer_temps_par_plage_hms(df)}"

@app.callback(
    dash.dependencies.Output('output-container-vitesseMoy', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_vitesseMoyenne(data):
    df = pd.DataFrame(data)
    return f"Vitesse moyenne: {vitesseMoyenne(df)} km/h"


@app.callback(
    dash.dependencies.Output('output-container-CO2', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_calculer_emissions_CO2(data):
    df = pd.DataFrame(data)
    dist = totalDist(df)
    
    emissions_CO2 = {
        'voiture': 89 , 
        'moto': 87, 
        'vélo': 6,
        'course à pieds': 0   
        
    }
    output_children = [] 

    for mode_transport, taux_CO2 in emissions_CO2.items():
        emissions_total = taux_CO2 * dist
        output_children.append(html.P(f"Pour {dist} km, les émissions de CO2 en utilisant un(e) {mode_transport} sont de {emissions_total} g/km"))
    
    return output_children

@app.callback(
    dash.dependencies.Output('output-container-caloVelo', 'children'),
    [dash.dependencies.Input('data', 'data'),
     dash.dependencies.Input('age-slider', 'value'),
     dash.dependencies.Input('weight-slider', 'value')]
)
def update_calories_burned(data, age, weight):
    df = pd.DataFrame(data)
    freqMoy = freqMoyenne(df)
    duree = totalTime(df)
    return f"calories brulées: {caloVelo(age, weight, freqMoy, duree)/200} kcal"

def update_map(data):
    df = pd.DataFrame(data)
    plot_route_on_map(df)
    return html.Iframe(srcDoc=open('assets/map_with_route.html', 'r').read(), width='60%', height='400',style={'display': 'block', 'margin': 'auto'})

if __name__ == '__main__':
    fig_hr, fig_temp, fig_elevation, fig_vitesse = plot_data_over_time(data)
    app.layout = generate_layout(fig_hr, fig_temp, fig_elevation, fig_vitesse)
    app.run_server(debug=True)
