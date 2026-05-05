import subprocess
import threading
import time
import sys

def start_fastapi():
    """Start FastAPI server in background"""
    try:
        print("🚀 Starting FastAPI server...")
        subprocess.run([sys.executable, "-m", "uvicorn", "lab_api:app", "--reload", "--port", "8000"])
    except Exception as e:
        print(f"❌ FastAPI server error: {e}")

def start_flet():
    """Start Flet application"""
    time.sleep(3)  # Wait for FastAPI to start
    try:
        print("📱 Starting Flet application...")
        subprocess.run([sys.executable, "lab_app.py"])
    except Exception as e:
        print(f"❌ Flet app error: {e}")

if __name__ == "__main__":
    print("🔬 Renewable Energy Lab - Starting Complete System")
    print("=" * 50)
    
    # Start FastAPI in background thread
    fastapi_thread = threading.Thread(target=start_fastapi, daemon=True)
    fastapi_thread.start()
    
    # Start Flet in main thread
    start_flet()
