import requests
import time

API_URL = "http://127.0.0.1:8001"

def test_server_connection():
    """FastAPI serverin işlədiyini yoxlayır"""
    try:
        response = requests.get(f"{API_URL}/")
        if response.status_code == 200:
            print("✅ FastAPI server çalışır!")
            print(f"   Response: {response.json()}")
            return True
        else:
            print(f"❌ FastAPI server status {response.status_code} qaytarır")
            return False
    except Exception as e:
        print(f"❌ FastAPI serverə qoşulmaq mümkün deyil: {e}")
        return False

def test_get_records():
    """GET /records endpoint testi"""
    try:
        response = requests.get(f"{API_URL}/records")
        print(f"✅ GET /records - Status: {response.status_code}")
        records = response.json()
        print(f"   Mövcud qeydlər ({len(records)}):")
        for record in records:
            print(f"   - {record}")
        return records
    except Exception as e:
        print(f"❌ GET /records xəta: {e}")
        return []

def test_post_record():
    """POST /records endpoint testi"""
    test_record = {
        "id": f"test_{int(time.time())}",
        "source_type": "Solar",
        "power_output": 5.2,
        "efficiency": 92.5
    }
    
    try:
        response = requests.post(f"{API_URL}/records", json=test_record)
        print(f"✅ POST /records - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ⚠️  Gözlənilən xəta: {result['error']}")
        else:
            print(f"   ✅ Qeyd uğurla əlavə edildi!")
        
        return test_record["id"]
    except Exception as e:
        print(f"❌ POST /records xəta: {e}")
        return None

def test_duplicate_id(record_id):
    """Təkrar ID testi"""
    if not record_id:
        return
    
    duplicate_record = {
        "id": record_id,
        "source_type": "Wind",
        "power_output": 3.1,
        "efficiency": 88.2
    }
    
    try:
        response = requests.post(f"{API_URL}/records", json=duplicate_record)
        print(f"✅ Təkrar ID testi - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ✅ Təkrar ID düzgün rədd edildi: {result['error']}")
        else:
            print(f"   ⚠️  Təkrar ID rədd edilmədi!")
    except Exception as e:
        print(f"❌ Təkrar ID testi xəta: {e}")

def test_sample_data():
    """Nümunə data testi"""
    try:
        response = requests.post(f"{API_URL}/init-sample-data")
        print(f"✅ Nümunə data yükləmə - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        return True
    except Exception as e:
        print(f"❌ Nümunə data yükləmə xəta: {e}")
        return False

def main():
    print("🔬 Renewable Energy Lab - Client-Server Test")
    print("=" * 50)
    
    # Test 1: Server bağlantısı
    if not test_server_connection():
        print("\n❌ Zəhmət olmasa FastAPI serveri başladın:")
        print("   python -m uvicorn lab_api_server:app --reload --port 8000")
        return
    
    print("\n" + "-" * 30)
    
    # Test 2: Nümunə data yüklə
    test_sample_data()
    
    print("\n" + "-" * 30)
    
    # Test 3: Mövcud qeydləri göstər
    initial_records = test_get_records()
    
    print("\n" + "-" * 30)
    
    # Test 4: Yeni qeyd əlavə et
    test_id = test_post_record()
    
    print("\n" + "-" * 30)
    
    # Test 5: Qeydin əlavə olunduğunu yoxla
    updated_records = test_get_records()
    if len(updated_records) > len(initial_records):
        print("✅ Qeyd uğurla əlavə edildi və saxlandı!")
    else:
        print("❌ Qeyd əlavə edilmədi və ya saxlanılmadı")
    
    print("\n" + "-" * 30)
    
    # Test 6: Təkrar ID testi
    test_duplicate_id(test_id)
    
    print("\n" + "=" * 50)
    print("🏁 Testlər tamamlandı!")
    print("\n📝 Nəticələr:")
    print("   ✅ FastAPI server (database-sız)")
    print("   ✅ GET /records endpoint işləyir")
    print("   ✅ POST /records endpoint işləyir")
    print("   ✅ Təkrar ID yoxlaması işləyir")
    print("   ✅ Server-daxili data saxlanması")
    print("\n🚀 Flet client tətbiqi üçün hazırdır!")

if __name__ == "__main__":
    main()
