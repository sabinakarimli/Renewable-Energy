import subprocess
import threading
import time
import sys

def start_fastapi_server():
    """FastAPI server-i arxada başladır"""
    try:
        print("🚀 FastAPI server başladılır...")
        subprocess.run([sys.executable, "-m", "uvicorn", "lab_api_server:app", "--reload", "--port", "8001"])
    except Exception as e:
        print(f"❌ FastAPI server xətası: {e}")

def start_flet_client():
    """Flet client tətbiqini başladır"""
    time.sleep(3)  # FastAPI-nin başlamasını gözlə
    try:
        print("📱 Flet client başladılır...")
        subprocess.run([sys.executable, "lab_client_app.py"])
    except Exception as e:
        print(f"❌ Flet client xətası: {e}")

if __name__ == "__main__":
    print("🔬 Renewable Energy Lab - Client-Server Sistemi")
    print("=" * 50)
    
    # FastAPI-ni arxada başlat
    fastapi_thread = threading.Thread(target=start_fastapi_server, daemon=True)
    fastapi_thread.start()
    
    # Flet client-i əsas thread-də başlat
    start_flet_client()
