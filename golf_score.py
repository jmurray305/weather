from collections import defaultdict


def group_by_day(hourly: dict) -> dict:
    """Groups hourly data into daily buckets keyed by date string (YYYY-MM-DD)."""
    days = defaultdict(list)

    times = hourly["time"]
    temps = hourly["temperature_2m"]
    winds = hourly["wind_speed_10m"]
    precips = hourly["precipitation_probability"]
    uvs = hourly["uv_index"]

    for i, timestamp in enumerate(times):
        date = timestamp.split("T")[0]  # extract YYYY-MM-DD from "YYYY-MM-DDTHH:MM"
        days[date].append({
            "temp": temps[i],
            "wind": winds[i],
            "precip": precips[i],
            "uv": uvs[i],
        })

    return days


def score_day(date: str, hours: list) -> dict:
    """
    Scores a single day for golf conditions on a 0–100 scale.

    Scoring weights:
        Temperature  (35pts)  → ideal 65–85°F
        Wind Speed   (25pts)  → ideal < 15 mph
        Precipitation(25pts)  → ideal < 20%
        UV Index     (15pts)  → ideal < 8
    """
    # --- Midday hours only (9 AM – 5 PM = indices 9–17) for realistic golf window ---
    golf_hours = [h for i, h in enumerate(hours) if 9 <= i <= 17] or hours

    avg_temp = round(sum(h["temp"] for h in golf_hours) / len(golf_hours), 1)
    avg_wind = round(sum(h["wind"] for h in golf_hours) / len(golf_hours), 1)
    avg_precip = round(sum(h["precip"] for h in golf_hours) / len(golf_hours), 1)
    avg_uv = round(sum(h["uv"] for h in golf_hours) / len(golf_hours), 1)

    # --- Temperature score (35 pts) ---
    if 65 <= avg_temp <= 85:
        temp_score = 35  # perfect range
    elif 55 <= avg_temp < 65 or 85 < avg_temp <= 95:
        temp_score = 20  # acceptable
    else:
        temp_score = 0  # too hot or too cold

    # --- Wind score (25 pts) ---
    if avg_wind < 15:
        wind_score = 25
    elif avg_wind < 25:
        wind_score = 15
    elif avg_wind < 35:
        wind_score = 5
    else:
        wind_score = 0

    # --- Precipitation score (25 pts) ---
    if avg_precip < 20:
        precip_score = 25
    elif avg_precip < 50:
        precip_score = 10
    else:
        precip_score = 0

    # --- UV score (15 pts) ---
    if avg_uv < 3:
        uv_score = 10  # too low = cloudy/cold
    elif avg_uv <= 7:
        uv_score = 15  # ideal
    elif avg_uv <= 10:
        uv_score = 8  # bring sunscreen
    else:
        uv_score = 3  # dangerously high

    golf_score = temp_score + wind_score + precip_score + uv_score

    return {
        "date": date,
        "avg_temp": avg_temp,
        "avg_wind": avg_wind,
        "avg_precip": avg_precip,
        "avg_uv": avg_uv,
        "temp_score": temp_score,
        "wind_score": wind_score,
        "precip_score": precip_score,
        "uv_score": uv_score,
        "golf_score": golf_score,
    }
