import pandas as pd
import numpy as np
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

stations = [
    {"region": "San Francisco", "lat": 37.8, "lon": -122.4},
    {"region": "Oakland", "lat": 37.8, "lon": -122.3},
    {"region": "San Jose", "lat": 37.3, "lon": -121.9},
    {"region": "Fremont", "lat": 37.6, "lon": -122.0},
    {"region": "Berkeley", "lat": 37.9, "lon": -122.3},
    {"region": "Hayward", "lat": 37.7, "lon": -122.1},
    {"region": "Sunnyvale", "lat": 37.4, "lon": -122.0},
    {"region": "Milpitas", "lat": 37.4, "lon": -121.9},
    {"region": "Santa Clara", "lat": 37.4, "lon": -121.9},
    {"region": "Palo Alto", "lat": 37.4, "lon": -122.1},
    {"region": "Redwood City", "lat": 37.5, "lon": -122.2},
    {"region": "Daly City", "lat": 37.7, "lon": -122.5},
    {"region": "Concord", "lat": 37.9, "lon": -122.0},
    {"region": "Walnut Creek", "lat": 37.9, "lon": -122.1},
    {"region": "Livermore", "lat": 37.7, "lon": -121.8},
    {"region": "Pleasanton", "lat": 37.7, "lon": -121.9},
    {"region": "Mountain View", "lat": 37.4, "lon": -122.1},
    {"region": "San Mateo", "lat": 37.6, "lon": -122.3},
    {"region": "Union City", "lat": 37.6, "lon": -122.0},
    {"region": "Alameda", "lat": 37.8, "lon": -122.3}
]

n_rows = 15000
data_pems = []
for i in range(n_rows):
    st = random.choice(stations)
    data_pems.append({
        "StationID": random.randint(1000, 9999),
        "Lat": st["lat"] + random.uniform(-0.01, 0.01),
        "Lon": st["lon"] + random.uniform(-0.01, 0.01),
        "Freeway": random.choice([101, 280, 880, 680, 80]),
        "Direction": random.choice(["N", "S", "E", "W"]),
        "LaneType": random.choice(["ML", "HOV", "OR", "FR"]),
        "TotalFlow": random.randint(10, 500),
        "AvgOccupancy": round(random.uniform(0.01, 0.3), 3),
        "AvgSpeed": round(random.uniform(10.0, 75.0), 1)
    })

pd.DataFrame(data_pems).to_csv(os.path.join(BASE_DIR, "pems_5min_cleaned_with_location.csv"), index=False)

data_ml = []
for i in range(n_rows):
    data_ml.append({
        "freeway": random.choice([101, 280, 880, 680, 80]),
        "direction": random.choice(["N", "S", "E", "W"]),
        "lane_type": random.choice(["ML", "HOV", "OR", "FR"]),
        "flow": random.randint(10, 500),
        "occupancy": round(random.uniform(0.01, 0.3), 3),
        "region": random.choice(["San Francisco", "Oakland", "San Jose", "Fremont"]),
        "temperature": round(random.uniform(10.0, 30.0), 1),
        "windspeed": round(random.uniform(0.0, 20.0), 1),
        "weathercode": random.randint(0, 5),
        "incident_type": random.choice(["none", "accident", "roadwork", "congestion"]),
        "severity": random.choice(["none", "low", "medium", "high"]),
        "speed": round(random.uniform(10.0, 75.0), 1)
    })

pd.DataFrame(data_ml).to_csv(os.path.join(BASE_DIR, "traffic_weather_incidents.csv"), index=False)
