import csv
from datetime import datetime, timezone
import folium
import plotly.express as px
import numpy as np

def seconds_to_hms(seconds):
    """Convertit les secondes en heures, minutes, secondes."""
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

    m.save("map_with_route.html")  # Save the map to an HTML file

plot_route_on_map("SortieVeloMatin.csv")

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

    # Show interactive plots
    fig_hr.show()
    fig_temp.show()
    fig_elevation.show()

plot_data_over_time("SortieVeloMatin.csv")


def totalDist(data):
    a = data[0]
    b = data[-1]
    t = b["distCum"] - a["distCum"]
    return t

def totalTime(data):
    a = data[0]["tempsCum"]
    b = data[-1]["tempsCum"]
    return b-a

def freqMoyenne (data):
    return np.sum(data["freqCard"].values) / data["freqCard"].size

def caloVelo(age, poids, freqMoy, duree):
    return (age * 0.2017 - poids * 0.09036 + freqMoy * 0.6309 - 55.0969) * duree / 4.184  

