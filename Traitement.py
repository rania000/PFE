import gpxpy
import csv
from math import sqrt
from datetime import datetime, timezone
import folium
import matplotlib.pyplot as plt

def gpx_to_csv(fichierGpx, fichierCsv):
    with open(fichierGpx, 'r') as gpx_file:
        gpx = gpxpy.parse(gpx_file)

    with open(fichierCsv, 'w', newline='') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['latitude', 'longitude', 'elevation', 'temps', 'temperature', 'freqCardiaque'])

        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                        
                        data_row = [point.latitude, point.longitude, point.elevation, point.time]
    
                        extensions_data = point.extensions
                        temperature = None
                        freqCardiaque = None

                        if extensions_data:
                            for extension in extensions_data:
                                for child in extension.iterchildren():
                                    if child.tag.endswith('atemp'):
                                        temperature = child.text
                                    elif child.tag.endswith('hr'):
                                        freqCardiaque = child.text

                        data_row.extend([temperature, freqCardiaque])
                        csv_writer.writerow(data_row)

gpx_to_csv('sortieVeloMatin.gpx', 'SortieVeloMatin.csv')



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
print(f"La distance euclidienne entre les deux points est d'environ {distance:f} degrés.")

from math import radians, sin, cos, sqrt, atan2

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

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            lat, lon = float(line['latitude']), float(line['longitude'])

            coordinates.append([lat, lon])

    # Add a Polyline connecting all points
    folium.PolyLine(coordinates, color='blue').add_to(m)

    m.save('map_with_route.html')  # Save the map to an HTML file

gpx_to_csv('sortieVeloMatin.gpx', 'SortieVeloMatin.csv')
plot_route_on_map('SortieVeloMatin.csv')



def plot_data_over_time(csv_path):
    times = []
    heart_rates = []
    speeds = []

    with open(csv_path, 'r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            time_str = row['temps']
            time_format = "%Y-%m-%d %H:%M:%S%z"
            time = datetime.strptime(time_str, time_format).replace(tzinfo=timezone.utc)
            
            heart_rate = float(row.get('freqCardiaque', 0))
            speed = float(row.get('speed', 0))

            times.append(time)
            heart_rates.append(heart_rate)
            speeds.append(speed)

    # Plotting heart rate
    plt.figure(figsize=(12, 6))
    plt.subplot(2, 1, 1)
    plt.plot(times, heart_rates, label='Heart Rate (bpm)', color='blue')
    plt.title('Heart Rate Over Time')
    plt.xlabel('Time')
    plt.ylabel('Heart Rate (bpm)')
    plt.legend()

    # Plotting speed
    plt.subplot(2, 1, 2)
    plt.plot(times, speeds, label='Speed (m/s)', color='green')
    plt.title('Speed Over Time')
    plt.xlabel('Time')
    plt.ylabel('Speed (m/s)')
    plt.legend()

    plt.tight_layout()
    plt.show()
