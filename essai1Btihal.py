import gpxpy
import csv
import os

import pandas as pd
from math import radians, cos, sin, asin, sqrt


def seconds_to_hms(seconds):
    """Convertit les secondes en heures, minutes, secondes."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def estimate_cadence(distance_meters, total_seconds, step_length_m=0.8):
    """Estime la cadence de course en pas par minute."""
    total_steps = distance_meters / step_length_m  # Nombre total de pas
    cadence = total_steps / (total_seconds / 60)  # Pas par minute
    return cadence

def calculate_speed(distance_meters, total_seconds):
    """Calcule la vitesse en km/h."""
    if total_seconds == 0:
        return 0
    speed_m_s = distance_meters / total_seconds  # Vitesse en mètres par seconde
    speed_km_h = speed_m_s * 3.6  # Convertir en kilomètres par heure
    return speed_km_h

input_folder = "C:/Users/btiha/Desktop/University/S6/02-ProjetAnnuel/Data"
output_folder = "C:/Users/btiha/Desktop/University/S6/02-ProjetAnnuel/Data"

if not os.path.exists(output_folder):
    os.makedirs(output_folder)

gpx_files = [f for f in os.listdir(input_folder) if f.endswith('.gpx')]

for i, gpx_file in enumerate(gpx_files, start=1):
    input_gpx_file = os.path.join(input_folder, gpx_file)
    output_csv_file = os.path.join(output_folder, f'fichier{i}.csv')
    total_time_seconds = 0
    total_distance_meters = 0

    with open(input_gpx_file, 'r') as gpxfile:
        gpx = gpxpy.parse(gpxfile)
    
    with open(output_csv_file, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['latitude', 'longitude', 'elevation', 'time', 'speed_km_h', 'cadence'])

        for track in gpx.tracks:
            for segment in track.segments:
                segment_start_time = segment.points[0].time if segment.points else None
                segment_end_time = segment.points[-1].time if segment.points else None
                
                if segment_start_time and segment_end_time:
                    segment_time_seconds = (segment_end_time - segment_start_time).total_seconds()
                    total_time_seconds += segment_time_seconds
                
                total_distance_meters += segment.length_3d()

        cadence = estimate_cadence(total_distance_meters, total_time_seconds)
        speed_average_km_h = calculate_speed(total_distance_meters, total_time_seconds)  # Calcul de la vitesse moyenne

        for track in gpx.tracks:
            for segment in track.segments:
                for i in range(len(segment.points) - 1):
                    point1 = segment.points[i]
                    point2 = segment.points[i + 1]
                    distance = point1.distance_3d(point2)
                    time_diff = (point2.time - point1.time).total_seconds()
                    speed_km_h = calculate_speed(distance, time_diff) if time_diff > 0 else 0
                    writer.writerow([point1.latitude, point1.longitude, point1.elevation, point1.time, speed_km_h, cadence])

    total_distance_km = total_distance_meters / 1000
    file_name = os.path.basename(output_csv_file)
    print(f'\nLe fichier {file_name} a été créé avec succès. \nTemps total: {seconds_to_hms(total_time_seconds)}. \nDistance totale: {total_distance_km:.2f} km. \nCadence estimée: {cadence:.2f} pas/min. \nVitesse moyenne: {speed_average_km_h:.2f} km/h.')

print('\nLa conversion de tous les fichiers GPX en CSV est terminée.')


#######################################################################################################################


def haversine(lon1, lat1, lon2, lat2):
    """
    Calcule la distance entre deux points sur la terre donnés en latitude et longitude en kilomètres.
    """
    # Convertir les coordonnées en radians
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    
    # Formule Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a))
    r = 6371  # Rayon de la Terre en kilomètres
    return c * r

def calculate_info_from_csv(csv_file, lat1, long1, lat2, long2):
    # Lire le fichier CSV
    df = pd.read_csv(csv_file)
    
    # Trouver les indices des points les plus proches pour chaque coordonnée
    distances1 = (df['latitude'] - lat1)**2 + (df['longitude'] - long1)**2
    index1 = distances1.idxmin()
    
    distances2 = (df['latitude'] - lat2)**2 + (df['longitude'] - long2)**2
    index2 = distances2.idxmin()
    
    # Assurez-vous que index1 est le plus petit
    if index1 > index2:
        index1, index2 = index2, index1
    
    # Calculer les informations demandées à partir du segment
    segment = df.iloc[index1:index2+1]
    total_time_seconds = (pd.to_datetime(segment.iloc[-1]['time']) - pd.to_datetime(segment.iloc[0]['time'])).total_seconds()
    total_distance_meters = 0
    for i in range(len(segment) - 1):
        lat1, lon1 = segment.iloc[i]['latitude'], segment.iloc[i]['longitude']
        lat2, lon2 = segment.iloc[i+1]['latitude'], segment.iloc[i+1]['longitude']
        total_distance_meters += haversine(lon1, lat1, lon2, lat2) * 1000  # Convertir en mètres
    
    cadence = estimate_cadence(total_distance_meters, total_time_seconds)
    speed_average_km_h = calculate_speed(total_distance_meters, total_time_seconds)
    
    return {
        "total_time": seconds_to_hms(total_time_seconds),
        "total_distance_m": total_distance_meters,
        "cadence": cadence,
        "speed_average_km_h": speed_average_km_h
    }
    


# Exemple d'utilisation avec le fichier CSV généré
csv_file = r'C:\Users\btiha\Desktop\University\S6\02-ProjetAnnuel\Data\fichier1.csv' 
lat1, long1 = 49.472693,1.061305,  # Coordonnées du point de départ
lat2, long2 = 49.456723,1.069987  # Coordonnées du point d'arrivée

results = calculate_info_from_csv(csv_file, lat1, long1, lat2, long2)

# Affichage formaté des résultats
print("\nPoint de départ :" , lat1,"," , long1 )
print("Point d'arrivée :" , lat2,"," , long2 )
print(f"Temps total entre les points spécifiés : {results['total_time']}")
print(f"Distance totale entre les points spécifiés : {results['total_distance_m']:.2f} mètres")
print(f"Cadence estimée : {results['cadence']:.2f} pas/min")
print(f"Vitesse moyenne : {results['speed_average_km_h']:.2f} km/h")
