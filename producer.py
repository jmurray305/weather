import json
import time
import requests
from datetime import datetime
from kafka import KafkaProducer
from dotenv import load_dotenv
import os
load_dotenv()

producer = KafkaProducer(
    bootstrap_servers="localhost:9092",
    value_serializer=lambda v: json.dumps(v).encode("utf-8")
)



def extract():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": os.getenv("LAT"),
        "longitude": os.getenv("LON"),
        "hourly": [
            "temperature_2m",
            "wind_speed_10m",
            "precipitation_probability",
            "uv_index"
        ],
        "timezone": "America/Denver",
        "wind_speed_unit": "mph",
        "temperature_unit": "fahrenheit",
        "forecast_days": 7          # ✅ next week (7days) only
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def produce():
    print(f"[{datetime.now()}] Fetching 7-day forecast...")
    raw = extract()
    producer.send("weather_raw", raw)
    producer.flush()
    print("✅ Published 7-day weather forecast to Kafka")
    #time.sleep(86400)           # ✅ poll once daily (86400 seconds)

if __name__ == "__main__":
    produce()