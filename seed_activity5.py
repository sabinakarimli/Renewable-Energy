import random
import sqlite3
import string
from datetime import datetime, timedelta


DB_NAME = "renewable_energy_comprehensive.db"
USER_ID = "demo_user"


def main():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS solar_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            panel_id TEXT NOT NULL,
            power_output REAL NOT NULL,
            efficiency REAL NOT NULL,
            temperature REAL NOT NULL,
            irradiance REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            panel_type TEXT,
            orientation TEXT,
            tilt_angle REAL,
            cleaning_schedule TEXT,
            degradation_rate REAL
        )
    """)

    statuses = ["active", "maintenance", "offline", "degraded"]
    panel_types = ["Monocrystalline", "Polycrystalline", "Thin Film"]
    orientations = ["South", "South-East", "South-West", "West"]

    for number in range(1, 121):
        suffix = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
        timestamp = (datetime.now() - timedelta(hours=number)).isoformat()
        conn.execute(
            """
            INSERT OR IGNORE INTO solar_records (
                id, user_id, panel_id, power_output, efficiency, temperature,
                irradiance, status, timestamp, panel_type, orientation,
                tilt_angle, cleaning_schedule, degradation_rate
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                f"SOLAR-{number:03}",
                USER_ID,
                f"PANEL-{suffix}",
                round(random.uniform(3.5, 18.0), 2),
                round(random.uniform(0.72, 0.96), 3),
                round(random.uniform(19.0, 46.0), 1),
                round(random.uniform(520.0, 990.0), 1),
                random.choice(statuses),
                timestamp,
                random.choice(panel_types),
                random.choice(orientations),
                random.choice([20, 25, 30, 35]),
                random.choice(["weekly", "monthly", "quarterly"]),
                round(random.uniform(0.2, 0.9), 2),
            ),
        )

    conn.commit()
    conn.close()
    print("Seeded 120 solar records for demo_user.")


if __name__ == "__main__":
    main()
