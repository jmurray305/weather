import sqlite3

DB_PATH = "golf_forecast.db"

def init_db():
    """Creates the predictions table if it doesn't exist."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS golf_predictions (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                date          TEXT NOT NULL,
                avg_temp      REAL,
                avg_wind      REAL,
                avg_precip    REAL,
                avg_uv        REAL,
                temp_score    INTEGER,
                wind_score    INTEGER,
                precip_score  INTEGER,
                uv_score      INTEGER,
                golf_score    INTEGER,
                created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(date)  -- prevent duplicate entries for the same date
            )
        """)
        conn.commit()
    print("✅ Database initialized")

def save_prediction(p: dict):
    """Inserts or updates a daily golf prediction."""
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            INSERT INTO golf_predictions
                (date, avg_temp, avg_wind, avg_precip, avg_uv,
                 temp_score, wind_score, precip_score, uv_score, golf_score)
            VALUES
                (:date, :avg_temp, :avg_wind, :avg_precip, :avg_uv,
                 :temp_score, :wind_score, :precip_score, :uv_score, :golf_score)
            ON CONFLICT(date) DO UPDATE SET
                avg_temp      = excluded.avg_temp,
                avg_wind      = excluded.avg_wind,
                avg_precip    = excluded.avg_precip,
                avg_uv        = excluded.avg_uv,
                temp_score    = excluded.temp_score,
                wind_score    = excluded.wind_score,
                precip_score  = excluded.precip_score,
                uv_score      = excluded.uv_score,
                golf_score    = excluded.golf_score,
                created_at    = CURRENT_TIMESTAMP
        """, p)
        conn.commit()