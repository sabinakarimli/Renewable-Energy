import sqlite3
import os
import sys

DB_NAME = "renewable_energy_lab.db"

def reset_database():
    """Delete old database and create new one"""
    
    # Delete old database if it exists
    if os.path.exists(DB_NAME):
        try:
            os.remove(DB_NAME)
            print(f"✅ Old database '{DB_NAME}' deleted successfully")
        except Exception as e:
            print(f"❌ Error deleting old database: {e}")
            return False
    
    # Create new database with improved schema
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("""
        CREATE TABLE energy_records (
            id TEXT PRIMARY KEY,
            source_type TEXT NOT NULL,
            power_output REAL NOT NULL,
            efficiency REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
        """)
        
        # Add some sample data
        sample_records = [
            ("solar_001", "Solar", 5.2, 92.5, "active"),
            ("wind_001", "Wind", 3.8, 88.2, "active"), 
            ("battery_001", "Battery", 2.1, 95.0, "active"),
            ("solar_002", "Solar", 6.7, 91.8, "maintenance"),
            ("wind_002", "Wind", 4.3, 89.5, "active")
        ]
        
        conn.executemany(
            "INSERT INTO energy_records (id, source_type, power_output, efficiency, status) VALUES (?, ?, ?, ?, ?)",
            sample_records
        )
        
        conn.commit()
        conn.close()
        
        print(f"✅ New database '{DB_NAME}' created successfully")
        print(f"✅ Added {len(sample_records)} sample records")
        
        # Verify the database
        conn = sqlite3.connect(DB_NAME)
        conn.row_factory = sqlite3.Row
        rows = conn.execute("SELECT * FROM energy_records").fetchall()
        conn.close()
        
        print(f"\n📊 Database contents:")
        for row in rows:
            print(f"   - {dict(row)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating new database: {e}")
        return False

if __name__ == "__main__":
    print("🔄 Resetting Renewable Energy Lab Database")
    print("=" * 50)
    
    if reset_database():
        print("\n🎉 Database reset completed successfully!")
        print("🚀 Ready to start the FastAPI server:")
        print("   python -m uvicorn lab_api:app --reload --port 8000")
    else:
        print("\n❌ Database reset failed!")
        sys.exit(1)
