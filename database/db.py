import sqlite3
import hashlib
import os
import threading
from datetime import datetime

DB_PATH = "energy.db"
_db_lock = threading.Lock()

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()

    # Users cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            theme TEXT DEFAULT 'dark'
        )
    """)

    # Energy data cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS energy_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            solar_kwh REAL DEFAULT 0,
            wind_kwh REAL DEFAULT 0,
            consumption_kwh REAL DEFAULT 0,
            battery_percent REAL DEFAULT 0,
            grid_sold_kwh REAL DEFAULT 0,
            recorded_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    # Alerts cədvəli
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT NOT NULL,
            alert_type TEXT DEFAULT 'info',
            is_read INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# ── USER funksiyaları ──────────────────────────

def register_user(name, email, password):
    with _db_lock:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                (name, email, hash_password(password))
            )
            conn.commit()
            conn.close()
            return True, "Qeydiyyat uğurlu oldu!"
        except sqlite3.IntegrityError:
            return False, "Bu email artıq qeydiyyatdan keçib!"

def login_user(email, password):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=? AND password=?",
            (email, hash_password(password))
        )
        user = cursor.fetchone()
        conn.close()
        if user:
            return True, dict(user)
        return False, "Email və ya şifrə yanlışdır!"

def get_user_by_id(user_id):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id=?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return dict(user) if user else None

# ── ENERGY DATA funksiyaları ───────────────────

def insert_energy_data(user_id, solar, wind, consumption, battery, grid_sold):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO energy_data 
            (user_id, solar_kwh, wind_kwh, consumption_kwh, battery_percent, grid_sold_kwh)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, solar, wind, consumption, battery, grid_sold))
        conn.commit()
        conn.close()

def get_latest_energy(user_id):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM energy_data 
            WHERE user_id=? 
            ORDER BY recorded_at DESC LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else {
            "solar_kwh": 24.5,
            "wind_kwh": 12.3,
            "consumption_kwh": 18.7,
            "battery_percent": 78,
            "grid_sold_kwh": 6.2
        }

def get_energy_history(user_id, limit=7):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM energy_data 
            WHERE user_id=? 
            ORDER BY recorded_at DESC LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

# ── ALERTS funksiyaları ────────────────────────

def get_alerts(user_id):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM alerts 
            WHERE user_id=? 
            ORDER BY created_at DESC LIMIT 10
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

def add_alert(user_id, message, alert_type="info"):
    with _db_lock:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO alerts (user_id, message, alert_type) VALUES (?, ?, ?)",
            (user_id, message, alert_type)
        )
        conn.commit()
        conn.close()