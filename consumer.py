import json
from kafka import KafkaConsumer
from db import init_db, save_prediction
from golf_score import score_day, group_by_day
import json
from kafka import KafkaConsumer
from db import init_db, save_prediction
from golf_score import score_day, group_by_day

consumer = KafkaConsumer(
    "weather_raw",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="golf-predictor-group"
)


def run():
    init_db()
    print("🎧 Consumer listening on topic: weather_raw")

    for message in consumer:
        raw = message.value
        hourly = raw["hourly"]

        # Group hourly data into 3 daily summaries
        days = group_by_day(hourly)

        for date, hours in days.items():
            prediction = score_day(date, hours)
            save_prediction(prediction)
            status = "⛳ GREAT" if prediction["golf_score"] >= 70 else "⚠️  OKAY" if prediction[
                                                                                        "golf_score"] >= 40 else "POOR"
            print(
                f"  {status}  |  {date}"
                f"  |  Score: {prediction['golf_score']}/100"
                f"  |  Avg Temp: {prediction['avg_temp']}°F"
                f"  |  Avg Wind: {prediction['avg_wind']} mph"
                f"  |  Avg Rain%: {prediction['avg_precip']}%"
                f"  |  Avg UV: {prediction['avg_uv']}"
            )


if __name__ == "__main__":
    run()
consumer = KafkaConsumer(
    "weather_raw",
    bootstrap_servers="localhost:9092",
    value_deserializer=lambda v: json.loads(v.decode("utf-8")),
    auto_offset_reset="latest",
    group_id="golf-predictor-group"
)


def run():
    init_db()
    print("🎧 Consumer listening on topic: weather_raw")

    for message in consumer:
        raw = message.value
        hourly = raw["hourly"]

        # Group hourly data into 3 daily summaries
        days = group_by_day(hourly)

        for date, hours in days.items():
            prediction = score_day(date, hours)
            save_prediction(prediction)
            status = "⛳ GREAT" if prediction["golf_score"] >= 70 else "⚠️  OKAY" if prediction[
                                                                                        "golf_score"] >= 40 else "POOR"
            print(
                f"  {status}  |  {date}"
                f"  |  Score: {prediction['golf_score']}/100"
                f"  |  Avg Temp: {prediction['avg_temp']}°F"
                f"  |  Avg Wind: {prediction['avg_wind']} mph"
                f"  |  Avg Rain%: {prediction['avg_precip']}%"
                f"  |  Avg UV: {prediction['avg_uv']}"
            )


if __name__ == "__main__":
    run()
