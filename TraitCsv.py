import csv
from datetime import datetime, timezone
import folium
import plotly.express as px
import numpy as np
import pandas as pd

def seconds_to_hms(seconds):
    """Convertit les secondes en heures, minutes, secondes."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

def plot_route_on_map(csv_path):
    m = folium.Map(location=[49.47302, 1.06102], zoom_start=11)  
    coordinates = []  

    with open(csv_path, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for line in csv_reader:
            lat, lon = float(line["latitude"]), float(line["longitude"])
            coordinates.append([lat, lon])
            
    """Add a Polyline connecting all points"""
    folium.PolyLine(coordinates, color="blue").add_to(m)

    m.save("map_with_route.html") 


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

            heart_rate = float(row.get("freqCard", 0))
            temperature = float(row.get("temperature", 0))
            elevation = float(row.get("elevation", 0))

            times.append(time)
            heart_rates.append(heart_rate)
            temperatures.append(temperature)
            elevations.append(elevation)

    # Plotly Express pour des plots interactifs
    fig_hr = px.line(
        x=times,
        y=heart_rates,
        labels={"x": "temps", "y": "fréquence cardiaque (bpm)"},
        title="frequence cardiaque",
    )
   
    fig_temp = px.line(
        x=times,
        y=temperatures,
        labels={"x": "Temps", "y": "Temperature (°C)"},
        title="temperature",
    )
    fig_elevation = px.line(
        x=times,
        y=elevations,
        labels={"x": "temps", "y": "Elevation (m)"},
        title="elevation",
    )
    fig_hr.show()
    fig_temp.show()
    fig_elevation.show()


def totalDist(data):
    dist = data["distCum"].values
    a = dist[0]
    b = dist[-1]
    return int((b-a) / 1000)

def totalTime(data):
    b = data["tempsCum"].values
    return b[-1]

def vitesseMoyenne(data):
    dist = data["distCum"].values
    temps = data["tempsCum"].values
    d = dist[-1]
    t = temps[-1]
    return int((d / 1000) / (t / 3600))
    
# la durée sur des intervalles (5 plages) de freq card en fonction de min
def freqMoyenne (data):
    return int(np.sum(data["freqCard"].values) / data["freqCard"].size)

#Cette équation est basée sur un modèle linéaire qui combine ces facteurs pour estimer la dépense énergétique
def caloVelo(age, poids, freqMoy, duree):
    return int((age * 0.2017 - poids * 0.09036 + freqMoy * 0.6309 - 55.0969) * duree / 4.184 ) 

def caloRun(poids,duree,MET=11.5):
    return int(poids * (duree / 3600) * MET)

def calculer_temps_par_plage_hms(data):
    # Convertir la colonne 'temps' en datetime
    data['temps'] = pd.to_datetime(data['temps'])
    
    # Calculer les différences de temps en secondes
    data['diff_temps'] = data['temps'].diff().dt.total_seconds().fillna(0)
    
    # Définir les plages de fréquence
    plages = [(0, 50), (51, 100), (101, 150), (151, 200), (201, float('inf'))]
    
    # Initialiser un dictionnaire pour stocker le temps total par plage
    temps_par_plage = {f"{min}-{max if max != float('inf') else '>'}": 0 for min, max in plages}
    
    # Itérer sur chaque enregistrement pour classer et additionner les temps
    for _, row in data.iterrows():
        freq = row['freqCard']
        for min, max in plages:
            if min <= freq <= max or (max == float('inf') and freq > 200):
                temps_par_plage[f"{min}-{max if max != float('inf') else '>'}"] += row['diff_temps']
                break
    
    # Convertir les secondes en h:m:s
    temps_par_plage_hms = {k: seconds_to_hms(v) for k, v in temps_par_plage.items()}
                
    return temps_par_plage_hms

def calculer_emissions_CO2(distance):
    emissions_CO2 = {
        'voiture': 120,  # Exemple de valeur pour une voiture en g/km
        'moto': 80,       # Les vélos n'émettent pas de CO2
        'a_pied': 0      # La marche à pied n'émet pas de CO2
    }

    # Calculer les émissions de CO2 pour chaque mode de transport
    for mode_transport, taux_CO2 in emissions_CO2.items():
        emissions_total = taux_CO2 * distance
        print(f"Pour une distance de {distance} kilomètres, les émissions de CO2 en utilisant un(e) {mode_transport} sont de {emissions_total} grammes de CO2.")

