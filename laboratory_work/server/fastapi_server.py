from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict

app = FastAPI(title="Renewable Energy Lab API - Server Only")

# ── In-memory data storage (no database) ───────────────────────────
# Server-daxili data saxlanması
energy_records: Dict[str, Dict] = {}

# ── Pydantic model ─────────────────────────────────────
class EnergyRecord(BaseModel):
    id: str
    source_type: str
    power_output: float
    efficiency: float

# ── GET: return all records ────────────────────────────
@app.get("/records")
def get_records():
    """Bütün enerji qeydlərini qaytarır"""
    return list(energy_records.values())

# ── POST: add new record ───────────────────────────────
@app.post("/records")
def add_record(record: EnergyRecord):
    """Yeni enerji qeydi əlavə edir"""
    if record.id in energy_records:
        return {"error": f"ID '{record.id}' already exists"}
    
    # Server-daxili data saxlanması
    energy_records[record.id] = {
        "id": record.id,
        "source_type": record.source_type,
        "power_output": record.power_output,
        "efficiency": record.efficiency,
        "status": "active"
    }
    
    return {"message": "Record added successfully", "record": energy_records[record.id]}

# ── GET: single record ───────────────────────────────
@app.get("/records/{record_id}")
def get_record(record_id: str):
    """Tək qeydi qaytarır"""
    if record_id not in energy_records:
        return {"error": f"ID '{record_id}' not found"}
    
    return energy_records[record_id]

# ── PUT: update record ───────────────────────────────
@app.put("/records/{record_id}")
def update_record(record_id: str, record: EnergyRecord):
    """Qeydi yeniləyir"""
    if record_id not in energy_records:
        return {"error": f"ID '{record_id}' not found"}
    
    # Update record in memory
    energy_records[record_id] = {
        "id": record_id,
        "source_type": record.source_type,
        "power_output": record.power_output,
        "efficiency": record.efficiency,
        "status": "active"
    }
    
    return {"message": f"Record '{record_id}' updated successfully", "record": energy_records[record_id]}

# ── DELETE: remove record ─────────────────────────────
@app.delete("/records/{record_id}")
def delete_record(record_id: str):
    """Qeydi silir"""
    if record_id not in energy_records:
        return {"error": f"ID '{record_id}' not found"}
    
    deleted_record = energy_records[record_id]
    del energy_records[record_id]
    return {"message": f"Record '{record_id}' deleted successfully", "deleted_record": deleted_record}

# ── PATCH: partial update ───────────────────────────
@app.patch("/records/{record_id}")
def patch_record(record_id: str, record_update: dict):
    """Qeydi qismən yeniləyir"""
    if record_id not in energy_records:
        return {"error": f"ID '{record_id}' not found"}
    
    # Update only provided fields
    current_record = energy_records[record_id]
    for key, value in record_update.items():
        if key in ["source_type", "power_output", "efficiency", "status"]:
            current_record[key] = value
    
    return {"message": f"Record '{record_id}' patched successfully", "record": current_record}

# ── Health check ───────────────────────────────────────
@app.get("/")
def health_check():
    """Serverin işlədiyini yoxlayır"""
    return {
        "status": "API server is running",
        "total_records": len(energy_records),
        "storage_type": "in-memory (no database)"
    }

# ── Sample data for testing ─────────────────────────────
@app.post("/init-sample-data")
def init_sample_data():
    """Test üçün nümunə data əlavə edir"""
    sample_data = [
        {"id": "solar_001", "source_type": "Solar", "power_output": 5.2, "efficiency": 92.5},
        {"id": "wind_001", "source_type": "Wind", "power_output": 3.8, "efficiency": 88.2},
        {"id": "battery_001", "source_type": "Battery", "power_output": 2.1, "efficiency": 95.0}
    ]
    
    for record in sample_data:
        if record["id"] not in energy_records:
            energy_records[record["id"]] = {
                **record,
                "status": "active"
            }
    
    return {"message": f"Added {len(sample_data)} sample records", "total": len(energy_records)}
