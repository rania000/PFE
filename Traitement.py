import gpxpy
import csv
from math import sqrt
from datetime import datetime, timezone
from math import atan2, cos, radians, sin
import folium
import plotly.express as px


def gpx_to_csv(fichierGpx, fichierCsv):
    with open(fichierGpx, "r") as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    with open(fichierCsv, "w", newline="") as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(
            [
                "latitude",
                "longitude",
                "elevation",
                "temps",
                "temperature",
                "freqCardiaque",
            ]
        )

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:

                    data_row = [
                        point.latitude,
                        point.longitude,
                        point.elevation,
                        point.time,
                    ]

                    extensions_data = point.extensions
                    temperature = None
                    freqCardiaque = None

                    if extensions_data:
                        for extension in extensions_data:
                            for child in extension.iterchildren():
                                if child.tag.endswith("atemp"):
                                    temperature = child.text
                                elif child.tag.endswith("hr"):
                                    freqCardiaque = child.text
                                

                    data_row.extend([temperature, freqCardiaque])
                    csv_writer.writerow(data_row)


gpx_to_csv("sortieVeloMatin.gpx", "SortieVeloMatin.csv")


def euclidean_distance(lat1, lon1, lat2, lon2):
    # Calculer les écarts entre les coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Distance euclidienne
    distance = sqrt(dlat**2 + dlon**2)

    return distance


# Exemple d'utilisation avec deux points géographiques
lat1, lon1 = 49.47302, 1.06102
lat2, lon2 = 49.47266, 1.06143

distance = euclidean_distance(lat1, lon1, lat2, lon2)
print(
    f"La distance euclidienne entre les deux points est d'environ {distance:f} degrés."
)


def haversine_distance(lat1, lon1, lat2, lon2):
    # Convertir les coordonnées degrés décimaux en radians
    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    # Calculer les écarts entre les coordonnées
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    # Formule haversine
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    # Rayon de la Terre en kilomètres (approximatif)
    radius_earth_km = 6371.0

    # Calculer la distance
    distance = radius_earth_km * c

    return distance


# Exemple d'utilisation avec deux points géographiques
lat1, lon1 = 49.47302, 1.06102
lat2, lon2 = 49.47266, 1.06143

distance = haversine_distance(lat1, lon1, lat2, lon2)
print(f"La distance entre les deux points est d'environ {distance:.2f} kilomètres.")


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


gpx_to_csv("sortieVeloMatin.gpx", "SortieVeloMatin.csv")
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
