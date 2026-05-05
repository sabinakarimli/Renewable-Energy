from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3

app = FastAPI(title="Renewable Energy Lab API")

DB_NAME = "renewable_energy_lab.db"

# ── Database helpers ───────────────────────────────────
def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS energy_records (
        id TEXT PRIMARY KEY,
        source_type TEXT NOT NULL,
        power_output REAL NOT NULL,
        efficiency REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        status TEXT DEFAULT 'active'
    )
    """)
    conn.commit()
    conn.close()

init_db()

# ── Pydantic model ─────────────────────────────────────
class EnergyRecord(BaseModel):
    id: str
    source_type: str
    power_output: float
    efficiency: float

# ── GET: return all records ────────────────────────────
@app.get("/records")
def get_records():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM energy_records ORDER BY id").fetchall()
    conn.close()
    return [dict(row) for row in rows]

# ── POST: add new record ───────────────────────────────
@app.post("/records")
def add_record(record: EnergyRecord):
    try:
        conn = get_connection()
        conn.execute(
            "INSERT INTO energy_records (id, source_type, power_output, efficiency) VALUES (?, ?, ?, ?)",
            (record.id, record.source_type, record.power_output, record.efficiency)
        )
        conn.commit()
        conn.close()
        return {"message": "Record added successfully", "record": record}
    except sqlite3.IntegrityError:
        return {"error": f"ID '{record.id}' already exists"}

# ── Health check ───────────────────────────────────────
@app.get("/")
def health_check():
    return {"status": "API is running", "database": DB_NAME}
