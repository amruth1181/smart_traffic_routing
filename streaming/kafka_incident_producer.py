import os
import pandas as pd
import random
import json
import time
from datetime import datetime
from kafka import KafkaProducer

# ✅ Load lat/lon from traffic file
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(BASE_DIR, 'pems_5min_cleaned_with_location.csv'))
gps_locations = df[['Lat', 'Lon']].drop_duplicates().sample(10).values.tolist()

# ✅ Incident types and severity levels
incident_types = ['accident', 'roadwork', 'congestion']
severities = ['low', 'medium', 'high']

# ✅ Kafka Producer
producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# ✅ Real-time incident stream
while True:
    lat, lon = random.choice(gps_locations)
    incident = {
        "timestamp": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
        "type": random.choice(incident_types),
        "severity": random.choice(severities),
        "location": {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6)
        },
        "description": "Simulated incident at Bay Area location"
    }

    print(f"🚧 Sending incident: {incident}")
    producer.send("traffic-incidents", value=incident)
    time.sleep(5)
