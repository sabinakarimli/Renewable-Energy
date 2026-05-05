import asyncio
import math
import random
from datetime import datetime

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

app = FastAPI(title="Renewable Energy WS")


def _payload() -> dict:
    hour = datetime.now().hour
    solar_base = max(0, 180 * math.sin(math.pi * (hour - 6) / 14)) if 6 <= hour <= 20 else 0
    solar = round(max(0, min(200, solar_base + random.uniform(-8, 8))), 1)
    wind = round(max(0, min(150, 70 + random.uniform(-20, 20))), 1)
    consumption = round(max(50, min(250, 140 + random.uniform(-30, 30))), 1)
    grid = round(max(0, min(100, 30 + random.uniform(-10, 10))), 1)
    battery = round(max(5, min(100, 75 + random.uniform(-8, 8))), 1)
    efficiency = round(max(85, min(99, 94 + random.uniform(-2, 2))), 1)
    co2_saved = round(max(8, min(25, 12 + random.uniform(-2, 2))), 1)
    revenue = round(max(200, min(400, 280 + random.uniform(-20, 20))), 1)
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "solar_kwh": solar,
        "wind_kwh": wind,
        "consumption_kwh": consumption,
        "battery_percent": battery,
        "grid_sold_kwh": grid,
        "efficiency": efficiency,
        "co2_saved": co2_saved,
        "revenue": revenue,
    }


@app.get("/health")
def health():
    return {"ok": True}


@app.websocket("/ws/energy")
async def ws_energy(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(_payload())
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        return
