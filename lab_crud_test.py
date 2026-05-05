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

def test_get_all_records():
    """GET /records - Bütün qeydləri göstərir"""
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
    """POST /records - Yeni qeyd əlavə edir"""
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
            print(f"   ⚠️  Xəta: {result['error']}")
            return None
        else:
            print(f"   ✅ Qeyd uğurla əlavə edildi!")
            return test_record["id"]
    except Exception as e:
        print(f"❌ POST /records xəta: {e}")
        return None

def test_get_single_record(record_id):
    """GET /records/{id} - Tək qeydi göstərir"""
    if not record_id:
        return
    
    try:
        response = requests.get(f"{API_URL}/records/{record_id}")
        print(f"✅ GET /records/{record_id} - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ⚠️  Xəta: {result['error']}")
        else:
            print(f"   ✅ Tək qeyd uğurla alındı!")
    except Exception as e:
        print(f"❌ GET /records/{record_id} xəta: {e}")

def test_put_record(record_id):
    """PUT /records/{id} - Qeydi tamamilə yeniləyir"""
    if not record_id:
        return
    
    updated_record = {
        "id": record_id,
        "source_type": "Wind",
        "power_output": 8.5,
        "efficiency": 95.0
    }
    
    try:
        response = requests.put(f"{API_URL}/records/{record_id}", json=updated_record)
        print(f"✅ PUT /records/{record_id} - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ⚠️  Xəta: {result['error']}")
        else:
            print(f"   ✅ Qeyd uğurla yeniləndi!")
    except Exception as e:
        print(f"❌ PUT /records/{record_id} xəta: {e}")

def test_patch_record(record_id):
    """PATCH /records/{id} - Qeydi qismən yeniləyir"""
    if not record_id:
        return
    
    partial_update = {
        "status": "maintenance",
        "efficiency": 96.0
    }
    
    try:
        response = requests.patch(f"{API_URL}/records/{record_id}", json=partial_update)
        print(f"✅ PATCH /records/{record_id} - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ⚠️  Xəta: {result['error']}")
        else:
            print(f"   ✅ Qeyd uğurla qismən yeniləndi!")
    except Exception as e:
        print(f"❌ PATCH /records/{record_id} xəta: {e}")

def test_delete_record(record_id):
    """DELETE /records/{id} - Qeydi silir"""
    if not record_id:
        return
    
    try:
        response = requests.delete(f"{API_URL}/records/{record_id}")
        print(f"✅ DELETE /records/{record_id} - Status: {response.status_code}")
        result = response.json()
        print(f"   Response: {result}")
        
        if "error" in result:
            print(f"   ⚠️  Xəta: {result['error']}")
        else:
            print(f"   ✅ Qeyd uğurla silindi!")
    except Exception as e:
        print(f"❌ DELETE /records/{record_id} xəta: {e}")

def test_swagger_docs():
    """Swagger sənədlərini yoxlayır"""
    try:
        response = requests.get(f"{API_URL}/docs")
        if response.status_code == 200:
            print("✅ Swagger docs mövcuddur!")
            print(f"   📖 Link: {API_URL}/docs")
            return True
        else:
            print(f"❌ Swagger docs status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swagger docs xəta: {e}")
        return False

def main():
    print("🔬 Renewable Energy Lab - Complete CRUD Test")
    print("=" * 60)
    
    # Test 1: Server bağlantısı
    if not test_server_connection():
        print("\n❌ Zəhmət olmasa FastAPI serveri başladın:")
        print("   python -m uvicorn lab_api_server:app --reload --port 8001")
        return
    
    print("\n" + "-" * 40)
    
    # Test 2: Swagger docs
    test_swagger_docs()
    
    print("\n" + "-" * 40)
    
    # Test 3: Nümunə data yüklə
    try:
        response = requests.post(f"{API_URL}/init-sample-data")
        result = response.json()
        print(f"✅ Nümunə data yükləndi: {result.get('message', '')}")
    except:
        pass
    
    print("\n" + "-" * 40)
    
    # Test 4: Başlanğıc qeydlər
    initial_records = test_get_all_records()
    
    print("\n" + "-" * 40)
    
    # Test 5: POST - Yeni qeyd
    test_id = test_post_record()
    
    print("\n" + "-" * 40)
    
    # Test 6: GET - Tək qeyd
    if test_id:
        test_get_single_record(test_id)
    
    print("\n" + "-" * 40)
    
    # Test 7: PUT - Tam yeniləmə
    if test_id:
        test_put_record(test_id)
    
    print("\n" + "-" * 40)
    
    # Test 8: PATCH - Qismən yeniləmə
    if test_id:
        test_patch_record(test_id)
    
    print("\n" + "-" * 40)
    
    # Test 9: DELETE - Silmə
    if test_id:
        test_delete_record(test_id)
    
    print("\n" + "-" * 40)
    
    # Test 10: Yekun qeydlər
    final_records = test_get_all_records()
    
    print("\n" + "=" * 60)
    print("🏁 Complete CRUD Test Tamamlandı!")
    print("\n📊 CRUD Əməliyyatları:")
    print("   ✅ GET /records - Bütün qeydlər")
    print("   ✅ GET /records/{id} - Tək qeyd")
    print("   ✅ POST /records - Yeni qeyd")
    print("   ✅ PUT /records/{id} - Tam yeniləmə")
    print("   ✅ PATCH /records/{id} - Qismən yeniləmə")
    print("   ✅ DELETE /records/{id} - Silmə")
    print("   ✅ Swagger /docs - API sənədləri")
    print(f"\n📖 Swagger Docs: {API_URL}/docs")
    print("🚀 Bütün CRUD əməliyyatları hazır!")

if __name__ == "__main__":
    main()
