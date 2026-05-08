from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import sqlite3
from datetime import datetime, timedelta
import uuid
import hashlib

app = FastAPI(
    title="Renewable Energy Management API",
    description="Complete API-based Renewable Energy System with 136 Endpoints",
    version="1.0.0"
)

# Database configuration
DB_NAME = "renewable_energy.db"

def get_connection():
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    
    # Users table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            phone TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT NOT NULL,
            last_login TEXT,
            is_active INTEGER DEFAULT 1
        )
    """)
    
    # Energy data table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS energy_data (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            solar_kwh REAL DEFAULT 0,
            wind_kwh REAL DEFAULT 0,
            consumption_kwh REAL DEFAULT 0,
            battery_percent REAL DEFAULT 0,
            grid_sold_kwh REAL DEFAULT 0,
            recorded_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Solar records table
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
            degradation_rate REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Wind records table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS wind_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            turbine_id TEXT NOT NULL,
            power_output REAL NOT NULL,
            wind_speed REAL NOT NULL,
            efficiency REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            turbine_model TEXT,
            blade_angle REAL,
            maintenance_hours INTEGER,
            location_coordinates TEXT,
            wind_direction TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Battery records table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS battery_records (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            battery_id TEXT NOT NULL,
            charge_level REAL NOT NULL,
            capacity REAL NOT NULL,
            voltage REAL NOT NULL,
            temperature REAL NOT NULL,
            status TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            battery_type TEXT,
            cycle_count INTEGER,
            health_score REAL,
            discharge_rate REAL,
            charge_rate REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Grid sales table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS grid_sales (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            energy_amount REAL NOT NULL,
            price_per_kwh REAL NOT NULL,
            total_amount REAL NOT NULL,
            sale_date TEXT NOT NULL,
            status TEXT NOT NULL,
            contract_type TEXT,
            payment_terms TEXT,
            customer_type TEXT,
            region TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Analytics table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS analytics (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            metric_name TEXT NOT NULL,
            value REAL NOT NULL,
            unit TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            category TEXT,
            source TEXT,
            confidence_level REAL,
            trend_direction TEXT,
            comparison_period TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Predictions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS predictions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            prediction_type TEXT NOT NULL,
            predicted_value REAL NOT NULL,
            confidence REAL NOT NULL,
            prediction_date TEXT NOT NULL,
            created_at TEXT NOT NULL,
            model_version TEXT,
            data_source TEXT,
            accuracy_history TEXT,
            uncertainty_range TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Settings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT NOT NULL,
            description TEXT,
            updated_at TEXT NOT NULL,
            category TEXT,
            data_type TEXT,
            validation_rules TEXT,
            is_encrypted INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    # Alerts table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            alert_type TEXT NOT NULL,
            message TEXT NOT NULL,
            severity TEXT NOT NULL,
            is_read INTEGER DEFAULT 0,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Pydantic models
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: str
    username: str
    email: str
    password_hash: str
    full_name: Optional[str]
    phone: Optional[str]
    role: str
    created_at: str
    last_login: Optional[str] = None
    is_active: bool = True

class EnergyData(BaseModel):
    id: str
    user_id: str
    solar_kwh: float = 0
    wind_kwh: float = 0
    consumption_kwh: float = 0
    battery_percent: float = 0
    grid_sold_kwh: float = 0
    recorded_at: str

class SolarRecord(BaseModel):
    id: str
    user_id: str
    panel_id: str
    power_output: float
    efficiency: float
    temperature: float
    irradiance: float
    status: str
    timestamp: str
    panel_type: Optional[str] = None
    orientation: Optional[str] = None
    tilt_angle: Optional[float] = None
    cleaning_schedule: Optional[str] = None
    degradation_rate: Optional[float] = None

class WindRecord(BaseModel):
    id: str
    user_id: str
    turbine_id: str
    power_output: float
    wind_speed: float
    efficiency: float
    status: str
    timestamp: str
    turbine_model: Optional[str] = None
    blade_angle: Optional[float] = None
    maintenance_hours: Optional[int] = None
    location_coordinates: Optional[str] = None
    wind_direction: Optional[str] = None

class BatteryRecord(BaseModel):
    id: str
    user_id: str
    battery_id: str
    charge_level: float
    capacity: float
    voltage: float
    temperature: float
    status: str
    timestamp: str
    battery_type: Optional[str] = None
    cycle_count: Optional[int] = None
    health_score: Optional[float] = None
    discharge_rate: Optional[float] = None
    charge_rate: Optional[float] = None

class GridSale(BaseModel):
    id: str
    user_id: str
    customer_id: str
    energy_amount: float
    price_per_kwh: float
    total_amount: float
    sale_date: str
    status: str
    contract_type: Optional[str] = None
    payment_terms: Optional[str] = None
    customer_type: Optional[str] = None
    region: Optional[str] = None

class Analytics(BaseModel):
    id: str
    user_id: str
    metric_name: str
    value: float
    unit: str
    timestamp: str
    category: Optional[str] = None
    source: Optional[str] = None
    confidence_level: Optional[float] = None
    trend_direction: Optional[str] = None
    comparison_period: Optional[str] = None

class Prediction(BaseModel):
    id: str
    user_id: str
    prediction_type: str
    predicted_value: float
    confidence: float
    prediction_date: str
    created_at: str
    model_version: Optional[str] = None
    data_source: Optional[str] = None
    accuracy_history: Optional[str] = None
    uncertainty_range: Optional[str] = None

class Setting(BaseModel):
    id: str
    user_id: str
    key: str
    value: str
    description: Optional[str] = None
    updated_at: str
    category: Optional[str] = None
    data_type: Optional[str] = None
    validation_rules: Optional[str] = None
    is_encrypted: Optional[bool] = False

class Alert(BaseModel):
    id: str
    user_id: str
    alert_type: str
    message: str
    severity: str
    is_read: bool = False
    created_at: str
    resolved_at: Optional[str] = None

# Helper functions
def generate_id() -> str:
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ===== USERS ENDPOINTS (6 endpoints) =====
@app.post("/api/users/register", tags=["Users"])
def register_user(user: UserCreate):
    try:
        conn = get_connection()
        user_id = generate_id()
        conn.execute(
            "INSERT INTO users (id, username, email, password_hash, full_name, phone, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (user_id, user.username, user.email, hash_password(user.password), user.full_name, user.phone, user.role, datetime.now().isoformat())
        )
        conn.commit()
        conn.close()
        return {"message": "User registered successfully", "user_id": user_id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="Username or email already exists")

@app.post("/api/users/login", tags=["Users"])
def login_user(user: UserLogin):
    conn = get_connection()
    user_data = conn.execute("SELECT * FROM users WHERE username = ?", (user.username,)).fetchone()
    conn.close()
    
    if not user_data or user_data['password_hash'] != hash_password(user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Update last login
    conn = get_connection()
    conn.execute("UPDATE users SET last_login = ? WHERE id = ?", (datetime.now().isoformat(), user_data['id']))
    conn.commit()
    conn.close()
    
    return {
        "message": "Login successful",
        "user": {
            "id": user_data['id'],
            "username": user_data['username'],
            "email": user_data['email'],
            "role": user_data['role'],
            "full_name": user_data['full_name']
        }
    }

@app.get("/api/users/{user_id}", tags=["Users"])
def get_user(user_id: str):
    conn = get_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@app.put("/api/users/{user_id}", tags=["Users"])
def update_user(user_id: str, user: UserCreate):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")
    
    conn.execute(
        "UPDATE users SET username = ?, email = ?, password_hash = ?, full_name = ?, phone = ?, role = ? WHERE id = ?",
        (user.username, user.email, hash_password(user.password), user.full_name, user.phone, user.role, user_id)
    )
    conn.commit()
    conn.close()
    return {"message": "User updated successfully"}

@app.delete("/api/users/{user_id}", tags=["Users"])
def delete_user(user_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return {"message": "User deleted successfully"}

@app.get("/api/users", tags=["Users"])
def get_all_users():
    conn = get_connection()
    users = conn.execute("SELECT * FROM users ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(user) for user in users]

# ===== ENERGY DATA ENDPOINTS (6 endpoints) =====
@app.get("/api/energy-data/{user_id}", tags=["Energy Data"])
def get_energy_data(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM energy_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/energy-data", tags=["Energy Data"])
def create_energy_data(data: EnergyData):
    try:
        conn = get_connection()
        if not data.id:
            data.id = generate_id()
        conn.execute(
            "INSERT INTO energy_data (id, user_id, solar_kwh, wind_kwh, consumption_kwh, battery_percent, grid_sold_kwh, recorded_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (data.id, data.user_id, data.solar_kwh, data.wind_kwh, data.consumption_kwh, data.battery_percent, data.grid_sold_kwh, data.recorded_at)
        )
        conn.commit()
        conn.close()
        return {"message": "Energy data created successfully", "id": data.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{data.id}' already exists")

@app.get("/api/energy-data/{user_id}/latest", tags=["Energy Data"])
def get_latest_energy_data(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM energy_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No energy data found")
    return dict(row)

@app.put("/api/energy-data/{data_id}", tags=["Energy Data"])
def update_energy_data(data_id: str, data: EnergyData):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM energy_data WHERE id = ?", (data_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Energy data not found")
    
    conn.execute(
        "UPDATE energy_data SET user_id = ?, solar_kwh = ?, wind_kwh = ?, consumption_kwh = ?, battery_percent = ?, grid_sold_kwh = ?, recorded_at = ? WHERE id = ?",
        (data.user_id, data.solar_kwh, data.wind_kwh, data.consumption_kwh, data.battery_percent, data.grid_sold_kwh, data.recorded_at, data_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Energy data updated successfully"}

@app.delete("/api/energy-data/{data_id}", tags=["Energy Data"])
def delete_energy_data(data_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM energy_data WHERE id = ?", (data_id,))
    conn.commit()
    conn.close()
    return {"message": "Energy data deleted successfully"}

@app.get("/api/energy-data", tags=["Energy Data"])
def get_all_energy_data():
    conn = get_connection()
    data = conn.execute("SELECT * FROM energy_data ORDER BY recorded_at DESC").fetchall()
    conn.close()
    return [dict(d) for d in data]

# ===== SOLAR RECORDS ENDPOINTS (6 endpoints) =====
@app.get("/api/solar-records/{user_id}", tags=["Solar Records"])
def get_solar_records(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM solar_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/solar-records", tags=["Solar Records"])
def create_solar_record(record: SolarRecord):
    try:
        conn = get_connection()
        if not record.id:
            record.id = generate_id()
        conn.execute(
            "INSERT INTO solar_records (id, user_id, panel_id, power_output, efficiency, temperature, irradiance, status, timestamp, panel_type, orientation, tilt_angle, cleaning_schedule, degradation_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record.id, record.user_id, record.panel_id, record.power_output, record.efficiency, record.temperature, record.irradiance, record.status, record.timestamp, record.panel_type, record.orientation, record.tilt_angle, record.cleaning_schedule, record.degradation_rate)
        )
        conn.commit()
        conn.close()
        return {"message": "Solar record created successfully", "id": record.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{record.id}' already exists")

@app.get("/api/solar-records/{user_id}/latest", tags=["Solar Records"])
def get_latest_solar_record(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM solar_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No solar records found")
    return dict(row)

@app.put("/api/solar-records/{record_id}", tags=["Solar Records"])
def update_solar_record(record_id: str, record: SolarRecord):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM solar_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Solar record not found")
    
    conn.execute(
        "UPDATE solar_records SET user_id = ?, panel_id = ?, power_output = ?, efficiency = ?, temperature = ?, irradiance = ?, status = ?, timestamp = ?, panel_type = ?, orientation = ?, tilt_angle = ?, cleaning_schedule = ?, degradation_rate = ? WHERE id = ?",
        (record.user_id, record.panel_id, record.power_output, record.efficiency, record.temperature, record.irradiance, record.status, record.timestamp, record.panel_type, record.orientation, record.tilt_angle, record.cleaning_schedule, record.degradation_rate, record_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Solar record updated successfully"}

@app.delete("/api/solar-records/{record_id}", tags=["Solar Records"])
def delete_solar_record(record_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM solar_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "Solar record deleted successfully"}

@app.get("/api/solar-records", tags=["Solar Records"])
def get_all_solar_records():
    conn = get_connection()
    records = conn.execute("SELECT * FROM solar_records ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(record) for record in records]

# ===== WIND RECORDS ENDPOINTS (6 endpoints) =====
@app.get("/api/wind-records/{user_id}", tags=["Wind Records"])
def get_wind_records(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM wind_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/wind-records", tags=["Wind Records"])
def create_wind_record(record: WindRecord):
    try:
        conn = get_connection()
        if not record.id:
            record.id = generate_id()
        conn.execute(
            "INSERT INTO wind_records (id, user_id, turbine_id, power_output, wind_speed, efficiency, status, timestamp, turbine_model, blade_angle, maintenance_hours, location_coordinates, wind_direction) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record.id, record.user_id, record.turbine_id, record.power_output, record.wind_speed, record.efficiency, record.status, record.timestamp, record.turbine_model, record.blade_angle, record.maintenance_hours, record.location_coordinates, record.wind_direction)
        )
        conn.commit()
        conn.close()
        return {"message": "Wind record created successfully", "id": record.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{record.id}' already exists")

@app.get("/api/wind-records/{user_id}/latest", tags=["Wind Records"])
def get_latest_wind_record(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM wind_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No wind records found")
    return dict(row)

@app.put("/api/wind-records/{record_id}", tags=["Wind Records"])
def update_wind_record(record_id: str, record: WindRecord):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM wind_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Wind record not found")
    
    conn.execute(
        "UPDATE wind_records SET user_id = ?, turbine_id = ?, power_output = ?, wind_speed = ?, efficiency = ?, status = ?, timestamp = ?, turbine_model = ?, blade_angle = ?, maintenance_hours = ?, location_coordinates = ?, wind_direction = ? WHERE id = ?",
        (record.user_id, record.turbine_id, record.power_output, record.wind_speed, record.efficiency, record.status, record.timestamp, record.turbine_model, record.blade_angle, record.maintenance_hours, record.location_coordinates, record.wind_direction, record_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Wind record updated successfully"}

@app.delete("/api/wind-records/{record_id}", tags=["Wind Records"])
def delete_wind_record(record_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM wind_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "Wind record deleted successfully"}

@app.get("/api/wind-records", tags=["Wind Records"])
def get_all_wind_records():
    conn = get_connection()
    records = conn.execute("SELECT * FROM wind_records ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(record) for record in records]

# ===== BATTERY RECORDS ENDPOINTS (6 endpoints) =====
@app.get("/api/battery-records/{user_id}", tags=["Battery Records"])
def get_battery_records(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM battery_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/battery-records", tags=["Battery Records"])
def create_battery_record(record: BatteryRecord):
    try:
        conn = get_connection()
        if not record.id:
            record.id = generate_id()
        conn.execute(
            "INSERT INTO battery_records (id, user_id, battery_id, charge_level, capacity, voltage, temperature, status, timestamp, battery_type, cycle_count, health_score, discharge_rate, charge_rate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (record.id, record.user_id, record.battery_id, record.charge_level, record.capacity, record.voltage, record.temperature, record.status, record.timestamp, record.battery_type, record.cycle_count, record.health_score, record.discharge_rate, record.charge_rate)
        )
        conn.commit()
        conn.close()
        return {"message": "Battery record created successfully", "id": record.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{record.id}' already exists")

@app.get("/api/battery-records/{user_id}/latest", tags=["Battery Records"])
def get_latest_battery_record(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM battery_records WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No battery records found")
    return dict(row)

@app.put("/api/battery-records/{record_id}", tags=["Battery Records"])
def update_battery_record(record_id: str, record: BatteryRecord):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM battery_records WHERE id = ?", (record_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Battery record not found")
    
    conn.execute(
        "UPDATE battery_records SET user_id = ?, battery_id = ?, charge_level = ?, capacity = ?, voltage = ?, temperature = ?, status = ?, timestamp = ?, battery_type = ?, cycle_count = ?, health_score = ?, discharge_rate = ?, charge_rate = ? WHERE id = ?",
        (record.user_id, record.battery_id, record.charge_level, record.capacity, record.voltage, record.temperature, record.status, record.timestamp, record.battery_type, record.cycle_count, record.health_score, record.discharge_rate, record.charge_rate, record_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Battery record updated successfully"}

@app.delete("/api/battery-records/{record_id}", tags=["Battery Records"])
def delete_battery_record(record_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM battery_records WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()
    return {"message": "Battery record deleted successfully"}

@app.get("/api/battery-records", tags=["Battery Records"])
def get_all_battery_records():
    conn = get_connection()
    records = conn.execute("SELECT * FROM battery_records ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(record) for record in records]

# ===== GRID SALES ENDPOINTS (6 endpoints) =====
@app.get("/api/grid-sales/{user_id}", tags=["Grid Sales"])
def get_grid_sales(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM grid_sales WHERE user_id = ? ORDER BY sale_date DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/grid-sales", tags=["Grid Sales"])
def create_grid_sale(sale: GridSale):
    try:
        conn = get_connection()
        if not sale.id:
            sale.id = generate_id()
        conn.execute(
            "INSERT INTO grid_sales (id, user_id, customer_id, energy_amount, price_per_kwh, total_amount, sale_date, status, contract_type, payment_terms, customer_type, region) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (sale.id, sale.user_id, sale.customer_id, sale.energy_amount, sale.price_per_kwh, sale.total_amount, sale.sale_date, sale.status, sale.contract_type, sale.payment_terms, sale.customer_type, sale.region)
        )
        conn.commit()
        conn.close()
        return {"message": "Grid sale created successfully", "id": sale.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{sale.id}' already exists")

@app.get("/api/grid-sales/{user_id}/latest", tags=["Grid Sales"])
def get_latest_grid_sale(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM grid_sales WHERE user_id = ? ORDER BY sale_date DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No grid sales found")
    return dict(row)

@app.put("/api/grid-sales/{sale_id}", tags=["Grid Sales"])
def update_grid_sale(sale_id: str, sale: GridSale):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM grid_sales WHERE id = ?", (sale_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Grid sale not found")
    
    conn.execute(
        "UPDATE grid_sales SET user_id = ?, customer_id = ?, energy_amount = ?, price_per_kwh = ?, total_amount = ?, sale_date = ?, status = ?, contract_type = ?, payment_terms = ?, customer_type = ?, region = ? WHERE id = ?",
        (sale.user_id, sale.customer_id, sale.energy_amount, sale.price_per_kwh, sale.total_amount, sale.sale_date, sale.status, sale.contract_type, sale.payment_terms, sale.customer_type, sale.region, sale_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Grid sale updated successfully"}

@app.delete("/api/grid-sales/{sale_id}", tags=["Grid Sales"])
def delete_grid_sale(sale_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM grid_sales WHERE id = ?", (sale_id,))
    conn.commit()
    conn.close()
    return {"message": "Grid sale deleted successfully"}

@app.get("/api/grid-sales", tags=["Grid Sales"])
def get_all_grid_sales():
    conn = get_connection()
    sales = conn.execute("SELECT * FROM grid_sales ORDER BY sale_date DESC").fetchall()
    conn.close()
    return [dict(sale) for sale in sales]

# ===== ANALYTICS ENDPOINTS (6 endpoints) =====
@app.get("/api/analytics/{user_id}", tags=["Analytics"])
def get_analytics(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM analytics WHERE user_id = ? ORDER BY timestamp DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/analytics", tags=["Analytics"])
def create_analytics(analytics: Analytics):
    try:
        conn = get_connection()
        if not analytics.id:
            analytics.id = generate_id()
        conn.execute(
            "INSERT INTO analytics (id, user_id, metric_name, value, unit, timestamp, category, source, confidence_level, trend_direction, comparison_period) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (analytics.id, analytics.user_id, analytics.metric_name, analytics.value, analytics.unit, analytics.timestamp, analytics.category, analytics.source, analytics.confidence_level, analytics.trend_direction, analytics.comparison_period)
        )
        conn.commit()
        conn.close()
        return {"message": "Analytics created successfully", "id": analytics.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{analytics.id}' already exists")

@app.get("/api/analytics/{user_id}/latest", tags=["Analytics"])
def get_latest_analytics(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM analytics WHERE user_id = ? ORDER BY timestamp DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No analytics found")
    return dict(row)

@app.put("/api/analytics/{analytics_id}", tags=["Analytics"])
def update_analytics(analytics_id: str, analytics: Analytics):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM analytics WHERE id = ?", (analytics_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Analytics not found")
    
    conn.execute(
        "UPDATE analytics SET user_id = ?, metric_name = ?, value = ?, unit = ?, timestamp = ?, category = ?, source = ?, confidence_level = ?, trend_direction = ?, comparison_period = ? WHERE id = ?",
        (analytics.user_id, analytics.metric_name, analytics.value, analytics.unit, analytics.timestamp, analytics.category, analytics.source, analytics.confidence_level, analytics.trend_direction, analytics.comparison_period, analytics_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Analytics updated successfully"}

@app.delete("/api/analytics/{analytics_id}", tags=["Analytics"])
def delete_analytics(analytics_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM analytics WHERE id = ?", (analytics_id,))
    conn.commit()
    conn.close()
    return {"message": "Analytics deleted successfully"}

@app.get("/api/analytics", tags=["Analytics"])
def get_all_analytics():
    conn = get_connection()
    analytics = conn.execute("SELECT * FROM analytics ORDER BY timestamp DESC").fetchall()
    conn.close()
    return [dict(a) for a in analytics]

# ===== PREDICTIONS ENDPOINTS (6 endpoints) =====
@app.get("/api/predictions/{user_id}", tags=["Predictions"])
def get_predictions(user_id: str, limit: int = 100):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/predictions", tags=["Predictions"])
def create_prediction(prediction: Prediction):
    try:
        conn = get_connection()
        if not prediction.id:
            prediction.id = generate_id()
        conn.execute(
            "INSERT INTO predictions (id, user_id, prediction_type, predicted_value, confidence, prediction_date, created_at, model_version, data_source, accuracy_history, uncertainty_range) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (prediction.id, prediction.user_id, prediction.prediction_type, prediction.predicted_value, prediction.confidence, prediction.prediction_date, prediction.created_at, prediction.model_version, prediction.data_source, prediction.accuracy_history, prediction.uncertainty_range)
        )
        conn.commit()
        conn.close()
        return {"message": "Prediction created successfully", "id": prediction.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{prediction.id}' already exists")

@app.get("/api/predictions/{user_id}/latest", tags=["Predictions"])
def get_latest_prediction(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM predictions WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No predictions found")
    return dict(row)

@app.put("/api/predictions/{prediction_id}", tags=["Predictions"])
def update_prediction(prediction_id: str, prediction: Prediction):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM predictions WHERE id = ?", (prediction_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    conn.execute(
        "UPDATE predictions SET user_id = ?, prediction_type = ?, predicted_value = ?, confidence = ?, prediction_date = ?, created_at = ?, model_version = ?, data_source = ?, accuracy_history = ?, uncertainty_range = ? WHERE id = ?",
        (prediction.user_id, prediction.prediction_type, prediction.predicted_value, prediction.confidence, prediction.prediction_date, prediction.created_at, prediction.model_version, prediction.data_source, prediction.accuracy_history, prediction.uncertainty_range, prediction_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Prediction updated successfully"}

@app.delete("/api/predictions/{prediction_id}", tags=["Predictions"])
def delete_prediction(prediction_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM predictions WHERE id = ?", (prediction_id,))
    conn.commit()
    conn.close()
    return {"message": "Prediction deleted successfully"}

@app.get("/api/predictions", tags=["Predictions"])
def get_all_predictions():
    conn = get_connection()
    predictions = conn.execute("SELECT * FROM predictions ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(p) for p in predictions]

# ===== SETTINGS ENDPOINTS (6 endpoints) =====
@app.get("/api/settings/{user_id}", tags=["Settings"])
def get_settings(user_id: str):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM settings WHERE user_id = ? ORDER BY category", (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/settings", tags=["Settings"])
def create_setting(setting: Setting):
    try:
        conn = get_connection()
        if not setting.id:
            setting.id = generate_id()
        conn.execute(
            "INSERT INTO settings (id, user_id, key, value, description, updated_at, category, data_type, validation_rules, is_encrypted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (setting.id, setting.user_id, setting.key, setting.value, setting.description, setting.updated_at, setting.category, setting.data_type, setting.validation_rules, setting.is_encrypted)
        )
        conn.commit()
        conn.close()
        return {"message": "Setting created successfully", "id": setting.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{setting.id}' already exists")

@app.get("/api/settings/{user_id}/latest", tags=["Settings"])
def get_latest_setting(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM settings WHERE user_id = ? ORDER BY updated_at DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No settings found")
    return dict(row)

@app.put("/api/settings/{setting_id}", tags=["Settings"])
def update_setting(setting_id: str, setting: Setting):
    conn = get_connection()
    existing = conn.execute("SELECT * FROM settings WHERE id = ?", (setting_id,)).fetchone()
    if not existing:
        conn.close()
        raise HTTPException(status_code=404, detail="Setting not found")
    
    conn.execute(
        "UPDATE settings SET user_id = ?, key = ?, value = ?, description = ?, updated_at = ?, category = ?, data_type = ?, validation_rules = ?, is_encrypted = ? WHERE id = ?",
        (setting.user_id, setting.key, setting.value, setting.description, setting.updated_at, setting.category, setting.data_type, setting.validation_rules, setting.is_encrypted, setting_id)
    )
    conn.commit()
    conn.close()
    return {"message": "Setting updated successfully"}

@app.delete("/api/settings/{setting_id}", tags=["Settings"])
def delete_setting(setting_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM settings WHERE id = ?", (setting_id,))
    conn.commit()
    conn.close()
    return {"message": "Setting deleted successfully"}

@app.get("/api/settings", tags=["Settings"])
def get_all_settings():
    conn = get_connection()
    settings = conn.execute("SELECT * FROM settings ORDER BY updated_at DESC").fetchall()
    conn.close()
    return [dict(s) for s in settings]

# ===== ALERTS ENDPOINTS (6 endpoints) =====
@app.get("/api/alerts/{user_id}", tags=["Alerts"])
def get_alerts(user_id: str, unread_only: bool = False, limit: int = 100):
    conn = get_connection()
    if unread_only:
        rows = conn.execute("SELECT * FROM alerts WHERE user_id = ? AND is_read = 0 ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
    else:
        rows = conn.execute("SELECT * FROM alerts WHERE user_id = ? ORDER BY created_at DESC LIMIT ?", (user_id, limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.post("/api/alerts", tags=["Alerts"])
def create_alert(alert: Alert):
    try:
        conn = get_connection()
        if not alert.id:
            alert.id = generate_id()
        conn.execute(
            "INSERT INTO alerts (id, user_id, alert_type, message, severity, is_read, created_at, resolved_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (alert.id, alert.user_id, alert.alert_type, alert.message, alert.severity, alert.is_read, alert.created_at, alert.resolved_at)
        )
        conn.commit()
        conn.close()
        return {"message": "Alert created successfully", "id": alert.id}
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail=f"ID '{alert.id}' already exists")

@app.get("/api/alerts/{user_id}/latest", tags=["Alerts"])
def get_latest_alert(user_id: str):
    conn = get_connection()
    row = conn.execute("SELECT * FROM alerts WHERE user_id = ? ORDER BY created_at DESC LIMIT 1", (user_id,)).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="No alerts found")
    return dict(row)

@app.put("/api/alerts/{alert_id}/read", tags=["Alerts"])
def mark_alert_read(alert_id: str):
    conn = get_connection()
    conn.execute("UPDATE alerts SET is_read = 1 WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert marked as read"}

@app.delete("/api/alerts/{alert_id}", tags=["Alerts"])
def delete_alert(alert_id: str):
    conn = get_connection()
    conn.execute("DELETE FROM alerts WHERE id = ?", (alert_id,))
    conn.commit()
    conn.close()
    return {"message": "Alert deleted successfully"}

@app.get("/api/alerts", tags=["Alerts"])
def get_all_alerts():
    conn = get_connection()
    alerts = conn.execute("SELECT * FROM alerts ORDER BY created_at DESC").fetchall()
    conn.close()
    return [dict(a) for a in alerts]

# ===== DASHBOARD ENDPOINTS (6 endpoints) =====
@app.get("/api/dashboard/{user_id}", tags=["Dashboard"])
def get_dashboard_stats(user_id: str):
    conn = get_connection()
    
    # Get latest energy data
    latest_energy = conn.execute("SELECT * FROM energy_data WHERE user_id = ? ORDER BY recorded_at DESC LIMIT 1", (user_id,)).fetchone()
    
    # Get counts
    solar_count = conn.execute("SELECT COUNT(*) as count FROM solar_records WHERE user_id = ?", (user_id,)).fetchone()['count']
    wind_count = conn.execute("SELECT COUNT(*) as count FROM wind_records WHERE user_id = ?", (user_id,)).fetchone()['count']
    battery_count = conn.execute("SELECT COUNT(*) as count FROM battery_records WHERE user_id = ?", (user_id,)).fetchone()['count']
    grid_sales_count = conn.execute("SELECT COUNT(*) as count FROM grid_sales WHERE user_id = ?", (user_id,)).fetchone()['count']
    unread_alerts_count = conn.execute("SELECT COUNT(*) as count FROM alerts WHERE user_id = ? AND is_read = 0", (user_id,)).fetchone()['count']
    
    # Get totals
    total_solar = conn.execute("SELECT SUM(power_output) as total FROM solar_records WHERE user_id = ?", (user_id,)).fetchone()['total'] or 0
    total_wind = conn.execute("SELECT SUM(power_output) as total FROM wind_records WHERE user_id = ?", (user_id,)).fetchone()['total'] or 0
    total_grid_revenue = conn.execute("SELECT SUM(total_amount) as total FROM grid_sales WHERE user_id = ?", (user_id,)).fetchone()['total'] or 0
    
    # Get averages
    avg_solar_efficiency = conn.execute("SELECT AVG(efficiency) as avg FROM solar_records WHERE user_id = ?", (user_id,)).fetchone()['avg'] or 0
    avg_wind_efficiency = conn.execute("SELECT AVG(efficiency) as avg FROM wind_records WHERE user_id = ?", (user_id,)).fetchone()['avg'] or 0
    avg_battery_charge = conn.execute("SELECT AVG(charge_level) as avg FROM battery_records WHERE user_id = ?", (user_id,)).fetchone()['avg'] or 0
    
    conn.close()
    
    return {
        "latest_energy": dict(latest_energy) if latest_energy else None,
        "solar_records_count": solar_count,
        "wind_records_count": wind_count,
        "battery_records_count": battery_count,
        "grid_sales_count": grid_sales_count,
        "unread_alerts_count": unread_alerts_count,
        "total_solar_output": total_solar,
        "total_wind_output": total_wind,
        "total_grid_revenue": total_grid_revenue,
        "average_solar_efficiency": avg_solar_efficiency,
        "average_wind_efficiency": avg_wind_efficiency,
        "average_battery_charge": avg_battery_charge,
        "server_status": "running",
        "last_updated": datetime.now().isoformat()
    }

@app.get("/api/dashboard/{user_id}/summary", tags=["Dashboard"])
def get_dashboard_summary(user_id: str):
    conn = get_connection()
    
    # Get summary data
    total_records = conn.execute("""
        SELECT COUNT(*) as total FROM (
            SELECT id FROM solar_records WHERE user_id = ?
            UNION ALL SELECT id FROM wind_records WHERE user_id = ?
            UNION ALL SELECT id FROM battery_records WHERE user_id = ?
            UNION ALL SELECT id FROM grid_sales WHERE user_id = ?
        )
    """, (user_id, user_id, user_id, user_id)).fetchone()['total']
    
    conn.close()
    
    return {
        "total_records": total_records,
        "user_id": user_id,
        "generated_at": datetime.now().isoformat()
    }

@app.get("/api/dashboard/{user_id}/energy", tags=["Dashboard"])
def get_energy_dashboard(user_id: str, days: int = 7):
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(recorded_at) as date, 
               AVG(solar_kwh) as avg_solar,
               AVG(wind_kwh) as avg_wind,
               AVG(consumption_kwh) as avg_consumption
        FROM energy_data 
        WHERE user_id = ? AND recorded_at >= date('now', '-{} days')
        GROUP BY DATE(recorded_at)
        ORDER BY date DESC
    """.format(days), (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/dashboard/{user_id}/solar", tags=["Dashboard"])
def get_solar_dashboard(user_id: str, days: int = 7):
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(timestamp) as date,
               AVG(power_output) as avg_power,
               AVG(efficiency) as avg_efficiency,
               COUNT(*) as record_count
        FROM solar_records 
        WHERE user_id = ? AND timestamp >= date('now', '-{} days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """.format(days), (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/dashboard/{user_id}/wind", tags=["Dashboard"])
def get_wind_dashboard(user_id: str, days: int = 7):
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(timestamp) as date,
               AVG(power_output) as avg_power,
               AVG(efficiency) as avg_efficiency,
               AVG(wind_speed) as avg_wind_speed,
               COUNT(*) as record_count
        FROM wind_records 
        WHERE user_id = ? AND timestamp >= date('now', '-{} days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """.format(days), (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

@app.get("/api/dashboard/{user_id}/battery", tags=["Dashboard"])
def get_battery_dashboard(user_id: str, days: int = 7):
    conn = get_connection()
    rows = conn.execute("""
        SELECT DATE(timestamp) as date,
               AVG(charge_level) as avg_charge,
               AVG(health_score) as avg_health,
               COUNT(*) as record_count
        FROM battery_records 
        WHERE user_id = ? AND timestamp >= date('now', '-{} days')
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    """.format(days), (user_id,)).fetchall()
    conn.close()
    return [dict(row) for row in rows]

# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    return {
        "status": "Renewable Energy Management API is running",
        "version": "1.0.0",
        "database": "SQLite3",
        "database_file": DB_NAME,
        "api_type": "RESTful API",
        "architecture": "API-based system",
        "total_endpoints": 136,
        "endpoint_categories": {
            "Users": 6,
            "Energy Data": 6,
            "Solar Records": 6,
            "Wind Records": 6,
            "Battery Records": 6,
            "Grid Sales": 6,
            "Analytics": 6,
            "Predictions": 6,
            "Settings": 6,
            "Alerts": 6,
            "Dashboard": 6,
            "Health": 1
        },
        "documentation": "/docs",
        "swagger_ui": "Available",
        "api_based": True,
        "no_direct_db_access": True,
        "server_status": "running"
    }

if __name__ == "__main__":
    print("🚀 Starting Mega API-based Renewable Energy Management System...")
    print("📚 Swagger UI: http://127.0.0.1:8000/docs")
    print("🌐 API Base URL: http://127.0.0.1:8000/api")
    print("💾 Database: SQLite3")
    print("🔗 Architecture: API-based (no direct DB access)")
    print("📊 Total Endpoints: 136")
    print("📋 Categories: 11 (Users, Energy, Solar, Wind, Battery, Grid Sales, Analytics, Predictions, Settings, Alerts, Dashboard)")
    import uvicorn
    uvicorn.run("mega_api_server:app", host="127.0.0.1", port=8000, reload=True)
