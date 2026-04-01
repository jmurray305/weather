# ⛳ Golf Weather Forecast — Kafka Pipeline

A real-time data pipeline that fetches a 7-day weather forecast and predicts whether conditions are suitable for golf. The producer publishes raw weather data to a Kafka topic daily, and the consumer scores each day and writes results to a SQLite database.

---

## Architecture

```
Open-Meteo API
      │  (once daily via cron)
      ▼
 producer.py  ──── weather_raw topic ────▶  consumer.py
                        (Kafka)                  │
                                                 ▼
                                           golf_score.py
                                           (score each day 0–100)
                                                 │
                                                 ▼
                                      db.py → golf_forecast.db
```

---

## Project Structure

```
weather/
├── producer.py          # Fetches forecast from Open-Meteo and publishes to Kafka
├── consumer.py          # Listens on Kafka topic, scores days, writes to DB
├── golf_score.py        # Scoring logic — converts hourly data into daily golf scores
├── db.py                # SQLite setup and upsert logic
├── docker-compose.yml   # Zookeeper + Kafka services
├── requirements.txt     # Python dependencies
└── README.md
```

---

## Golf Scoring Breakdown

Each day is scored out of **100 points** based on midday hours (9 AM – 5 PM):

| Factor          | Weight | Ideal Condition         |
|-----------------|--------|-------------------------|
| Temperature     | 35 pts | 65°F – 85°F             |
| Wind Speed      | 25 pts | < 15 mph                |
| Precipitation   | 25 pts | < 20% chance            |
| UV Index        | 15 pts | 3 – 7 (not too low/high)|

| Score   | Verdict     |
|---------|-------------|
| 70–100  | ⛳ GREAT    |
| 40–69   | ⚠️  OKAY   |
| 0–39    | ❌ POOR     |

---

## Prerequisites

- Python 3.9+
- Docker + Docker Compose
- Anaconda (or any Python environment)

---

## Installation

**1. Clone the repo and navigate to the project folder:**
```bash
cd ~/Desktop/weather
```

**2. Install Python dependencies:**
```bash
pip install -r requirements.txt
```

**3. Start Kafka and Zookeeper:**
```bash
docker-compose up -d
```

Wait ~15 seconds for Kafka to fully boot, then confirm both containers are running:
```bash
docker ps
```

---

## Running the Pipeline

**Step 1 — Start the consumer (keep it running in the background):**
```bash
nohup /Users/justinmurray/opt/anaconda3/bin/python /Users/justinmurray/Desktop/weather/consumer.py >> /Users/justinmurray/Desktop/weather/consumer.log 2>&1 &
```

**Step 2 — Run the producer manually to test:**
```bash
python producer.py
```

You should see output like:
```
[2026-04-01 06:00:00] Fetching 7-day forecast...
✅ Published 7-day weather forecast to Kafka
⛳ GREAT  |  2026-04-01  |  Score: 82/100  |  Avg Temp: 74.2°F  |  Avg Wind: 8.3 mph  |  Avg Rain%: 5.0%  |  Avg UV: 6.1
⚠️  OKAY  |  2026-04-02  |  Score: 55/100  |  Avg Temp: 68.1°F  |  Avg Wind: 22.4 mph  |  Avg Rain%: 18.0%  |  Avg UV: 5.9
...
```

---

## Scheduling (Run Every Morning at 6 AM)

Add the producer to your crontab so it runs automatically every morning:

```bash
crontab -e
```

Add this line:
```bash
0 6 * * * /Users/justinmurray/opt/anaconda3/bin/python /Users/justinmurray/Desktop/weather/producer.py >> /Users/justinmurray/Desktop/weather/producer.log 2>&1
```

Verify it saved:
```bash
crontab -l
```

---

## Running the Consumer as a Persistent Background Service (macOS)

The consumer must run continuously to pick up Kafka messages. Use `launchd` to keep it alive across reboots and crashes:

```bash
nano ~/Library/LaunchAgents/com.weather.consumer.plist
```

Paste in:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.weather.consumer</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/justinmurray/opt/anaconda3/bin/python</string>
        <string>/Users/justinmurray/Desktop/weather/consumer.py</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/justinmurray/Desktop/weather/consumer.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/justinmurray/Desktop/weather/consumer.log</string>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.weather.consumer.plist
```

Useful commands:
```bash
launchctl unload ~/Library/LaunchAgents/com.weather.consumer.plist  # stop
launchctl load   ~/Library/LaunchAgents/com.weather.consumer.plist  # start
```

---

## Checking Logs

```bash
# Producer logs
cat /Users/justinmurray/Desktop/weather/producer.log

# Consumer logs
cat /Users/justinmurray/Desktop/weather/consumer.log

# Kafka logs
docker-compose logs kafka
```

---

## Querying the Database

Results are saved to `golf_forecast.db`. Query it with Python:

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect("golf_forecast.db")
df = pd.read_sql("SELECT * FROM golf_predictions ORDER BY date", conn)
print(df)
```

Or via the SQLite CLI:
```bash
sqlite3 golf_forecast.db "SELECT date, golf_score FROM golf_predictions ORDER BY date;"
```

---

## Data Source

Weather data is provided by the free [Open-Meteo API](https://open-meteo.com/) — no API key required.

**Parameters used:** `temperature_2m`, `wind_speed_10m`, `precipitation_probability`, `uv_index`
**Location:** Commerce City, CO (lat: 39.931889, lon: -104.875009)
**Forecast window:** 7 days
**Units:** Fahrenheit, mph

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `NoBrokersAvailable` | Kafka isn't ready yet — wait 15s and retry |
| `KAFKA_PROCESS_ROLES not set` | Pin Docker images to `7.4.0` (see docker-compose.yml) |
| `JSONDecodeError` on API call | Check network, add `response.raise_for_status()` |
| Consumer not receiving messages | Make sure consumer started before producer ran |
