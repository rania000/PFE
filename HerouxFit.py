import csv
from datetime import datetime, timezone
import dash
from dash import dcc, html
import plotly.express as px
import numpy as np
import folium
import pandas as pd
import dash_bootstrap_components as dbc
from TraitCsv import *

data = pd.read_csv("SortieVeloMatin.csv")
external_stylesheets = [dbc.themes.BOOTSTRAP]

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

def seconds_to_hms(seconds):
    """Convert seconds to hours, minutes, seconds."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def plot_route_on_map(csv_path):
    m = folium.Map(location=[49.47302, 1.06102], zoom_start=11)  # Create a folium map

    coordinates = []  # List to store coordinates for Polyline

    with open(csv_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            lat, lon = float(line["latitude"]), float(line["longitude"])
            coordinates.append([lat, lon])

    # Add a Polyline connecting all points
    folium.PolyLine(coordinates, color="blue").add_to(m)

    m.save("assets/map_with_route.html")  # Save the map to an HTML file

def plot_data_over_time(csv_path):
    times = []
    heart_rates = []
    temperatures = []
    elevations = []

    with open(csv_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            time_str = row["temps"]
            time_format = "%Y-%m-%d %H:%M:%S%z"
            time = datetime.strptime(time_str, time_format).replace(tzinfo=timezone.utc)

            heart_rate = float(row.get("freqCardiaque", 0))
            temperature = float(row.get("temperature", 0))
            elevation = float(row.get("elevation", 0))

            times.append(time)
            heart_rates.append(heart_rate)
            temperatures.append(temperature)
            elevations.append(elevation)

    # Create interactive plots using Plotly Express
    fig_hr = px.line(
        x=times,
        y=heart_rates,
        labels={"x": "Time", "y": "Heart Rate (bpm)"},
        title="Heart Rate Over Time",
    )
   
    fig_temp = px.line(
        x=times,
        y=temperatures,
        labels={"x": "Time", "y": "Temperature (°C)"},
        title="Temperature Over Time",
    )
    fig_elevation = px.line(
        x=times,
        y=elevations,
        labels={"x": "Time", "y": "Elevation (m)"},
        title="Elevation Over Time",
    )

    return fig_hr, fig_temp, fig_elevation

def generate_layout(fig_hr, fig_temp, fig_elevation):
    return html.Div([
        html.H1("Fitness Dashboard", className="text-center my-4"),
        dbc.Row([
            dbc.Col(dcc.Graph(figure=fig_hr), width=4),
            dbc.Col(dcc.Graph(figure=fig_temp), width=4),
            dbc.Col(dcc.Graph(figure=fig_elevation), width=4),
        ]),
        html.Div(id='map-container'),
        html.Div(id='output-container-totalDist'),
        html.Div(id='output-container-totalTime'),
        html.Div(id='output-container-freqMoyenne'),
        html.Div(id='output-container-caloVelo'),
        dcc.Store(id='data', storage_type='session', data={}),
    ])

@app.callback(
    dash.dependencies.Output('output-container-totalDist', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_total_distance(data):
    return f"Total Distance: {totalDist(data)}"

@app.callback(
    dash.dependencies.Output('output-container-totalTime', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_total_time(data):
    return f"Total Time: {seconds_to_hms(totalTime(data))}"

@app.callback(
    dash.dependencies.Output('output-container-freqMoyenne', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_average_frequency(data):
    return f"Average Frequency: {freqMoyenne(data)} bpm"

@app.callback(
    dash.dependencies.Output('output-container-caloVelo', 'children'),
    [dash.dependencies.Input('age', 'value'),
     dash.dependencies.Input('weight', 'value'),
     dash.dependencies.Input('data', 'data')]
)
def update_calories_burned(age, weight, data):
    freqMoy = freqMoyenne(data)
    duree = totalTime(data)
    return f"Calories Burned: {caloVelo(age, weight, freqMoy, duree)} kcal"

@app.callback(
    dash.dependencies.Output('map-container', 'children'),
    [dash.dependencies.Input('data', 'data')]
)
def update_map(data):
    plot_route_on_map("SortieVeloMatin.csv")
    return html.Iframe(srcDoc=open('assets/map_with_route.html', 'r').read(), width='100%', height='600')

if __name__ == '__main__':
    fig_hr, fig_temp, fig_elevation = plot_data_over_time("SortieVeloMatin.csv")
    app.layout = generate_layout(fig_hr, fig_temp, fig_elevation)
    app.run_server(debug=True)
