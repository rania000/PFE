import gpxpy
import csv
from math import sqrt
from math import atan2, cos, radians, sin

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
                "freqCard",
                "vitesseInst",
                "distCum",
                "tempsCum"
            ]
        )
        previous_point = None
        distCum = 0
        timeCum = 0
        for track in gpx.tracks:
            for segment in track.segments:
                for point in segment.points:
                    if previous_point:
                        # Calculer la distance et le temps entre le point actuel et le précédent
                        distance = haversine_distance(previous_point.longitude, previous_point.latitude, point.longitude, point.latitude) * 1000
                        time_diff = (point.time - previous_point.time).total_seconds()
                        timeCum += time_diff
                        # Calculer la vitesse instantanée si time_diff > 0, sinon 0
                        speed_instant_km_h = calculate_speed(distance, time_diff)
                        distCum += distance
                    else:
                        # Pour le premier point du segment
                        speed_instant_km_h = 0
                        distCum += 0
                    previous_point = point
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
                                
                     
                    data_row.extend([temperature, freqCardiaque,speed_instant_km_h,distCum,timeCum])
                    csv_writer.writerow(data_row)


gpx_to_csv("sortieVeloMatin.gpx", "SortieVeloMatin.csv")
gpx_to_csv('Course_pied_dans_l_apr_s_midi.gpx',"CoursePied.csv")
