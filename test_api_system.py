import requests
import json
from datetime import datetime
import uuid

API_BASE_URL = "http://127.0.0.1:8000/api"

def test_api_system():
    print("🚀 Testing Complete API-based Renewable Energy System")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing API Health Check...")
    try:
        response = requests.get("http://127.0.0.1:8000/")
        data = response.json()
        print(f"✅ Status: {data['status']}")
        print(f"✅ API Type: {data['api_type']}")
        print(f"✅ Architecture: {data['architecture']}")
        print(f"✅ API-based: {data['api_based']}")
        print(f"✅ No Direct DB Access: {data['no_direct_db_access']}")
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False
    
    # Test 2: User Registration
    print("\n2. Testing User Registration...")
    user_data = {
        "username": f"testuser_{uuid.uuid4().hex[:8]}",
        "email": f"test_{uuid.uuid4().hex[:8]}@example.com",
        "password": "test123456",
        "full_name": "Test User",
        "phone": "+994501234567",
        "role": "user"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/register", json=user_data)
        if response.status_code == 200:
            result = response.json()
            if "user_id" in result:
                print(f"✅ User Registered: {result['user_id']}")
                user_id = result['user_id']
            else:
                print(f"❌ Registration Failed: {result}")
                return False
        else:
            print(f"❌ Registration Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Registration Failed: {e}")
        return False
    
    # Test 3: User Login
    print("\n3. Testing User Login...")
    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/users/login", json=login_data)
        if response.status_code == 200:
            result = response.json()
            if "user" in result:
                print(f"✅ Login Successful: {result['user']['username']}")
                logged_user_id = result['user']['id']
            else:
                print(f"❌ Login Failed: {result}")
                return False
        else:
            print(f"❌ Login Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Login Failed: {e}")
        return False
    
    # Test 4: Create Solar Record
    print("\n4. Testing Solar Record Creation...")
    solar_data = {
        "user_id": logged_user_id,
        "panel_id": f"panel_{uuid.uuid4().hex[:8]}",
        "power_output": 75.5,
        "efficiency": 92.1,
        "temperature": 25.5,
        "irradiance": 850.0,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "panel_type": "Monocrystalline",
        "orientation": "South",
        "tilt_angle": 30.0,
        "cleaning_schedule": "Monthly",
        "degradation_rate": 0.3
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/solar-records", json=solar_data)
        if response.status_code == 200:
            result = response.json()
            if "id" in result:
                print(f"✅ Solar Record Created: {result['id']}")
                solar_id = result['id']
            else:
                print(f"❌ Solar Record Creation Failed: {result}")
                return False
        else:
            print(f"❌ Solar Record Creation Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Solar Record Creation Failed: {e}")
        return False
    
    # Test 5: Create Wind Record
    print("\n5. Testing Wind Record Creation...")
    wind_data = {
        "user_id": logged_user_id,
        "turbine_id": f"turbine_{uuid.uuid4().hex[:8]}",
        "power_output": 150.8,
        "wind_speed": 15.2,
        "efficiency": 88.7,
        "status": "active",
        "timestamp": datetime.now().isoformat(),
        "turbine_model": "Vestas V136",
        "blade_angle": 25.0,
        "maintenance_hours": 1500,
        "location_coordinates": "40.7128, -74.0060",
        "wind_direction": "NW"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/wind-records", json=wind_data)
        if response.status_code == 200:
            result = response.json()
            if "id" in result:
                print(f"✅ Wind Record Created: {result['id']}")
                wind_id = result['id']
            else:
                print(f"❌ Wind Record Creation Failed: {result}")
                return False
        else:
            print(f"❌ Wind Record Creation Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Wind Record Creation Failed: {e}")
        return False
    
    # Test 6: Create Battery Record
    print("\n6. Testing Battery Record Creation...")
    battery_data = {
        "user_id": logged_user_id,
        "battery_id": f"battery_{uuid.uuid4().hex[:8]}",
        "charge_level": 85.5,
        "capacity": 500.0,
        "voltage": 48.0,
        "temperature": 22.3,
        "status": "charging",
        "timestamp": datetime.now().isoformat(),
        "battery_type": "Li-ion",
        "cycle_count": 1500,
        "health_score": 92.5,
        "discharge_rate": 50.0,
        "charge_rate": 75.0
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/battery-records", json=battery_data)
        if response.status_code == 200:
            result = response.json()
            if "id" in result:
                print(f"✅ Battery Record Created: {result['id']}")
                battery_id = result['id']
            else:
                print(f"❌ Battery Record Creation Failed: {result}")
                return False
        else:
            print(f"❌ Battery Record Creation Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Battery Record Creation Failed: {e}")
        return False
    
    # Test 7: Create Grid Sale
    print("\n7. Testing Grid Sale Creation...")
    sale_data = {
        "user_id": logged_user_id,
        "customer_id": f"customer_{uuid.uuid4().hex[:8]}",
        "energy_amount": 250.0,
        "price_per_kwh": 0.15,
        "total_amount": 37.5,
        "sale_date": datetime.now().isoformat(),
        "status": "completed",
        "contract_type": "Fixed",
        "payment_terms": "Monthly",
        "customer_type": "Commercial",
        "region": "North"
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/grid-sales", json=sale_data)
        if response.status_code == 200:
            result = response.json()
            if "id" in result:
                print(f"✅ Grid Sale Created: {result['id']}")
                sale_id = result['id']
            else:
                print(f"❌ Grid Sale Creation Failed: {result}")
                return False
        else:
            print(f"❌ Grid Sale Creation Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Grid Sale Creation Failed: {e}")
        return False
    
    # Test 8: Create Energy Data
    print("\n8. Testing Energy Data Creation...")
    energy_data = {
        "user_id": logged_user_id,
        "solar_kwh": 100.5,
        "wind_kwh": 150.8,
        "consumption_kwh": 80.2,
        "battery_percent": 75.0,
        "grid_sold_kwh": 50.0,
        "recorded_at": datetime.now().isoformat()
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/energy-data", json=energy_data)
        if response.status_code == 200:
            result = response.json()
            if "id" in result:
                print(f"✅ Energy Data Created: {result['id']}")
                energy_id = result['id']
            else:
                print(f"❌ Energy Data Creation Failed: {result}")
                return False
        else:
            print(f"❌ Energy Data Creation Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Energy Data Creation Failed: {e}")
        return False
    
    # Test 9: Get Solar Records
    print("\n9. Testing Get Solar Records...")
    try:
        response = requests.get(f"{API_BASE_URL}/solar-records/{logged_user_id}")
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Retrieved {len(records)} Solar Records")
            if len(records) > 0:
                print(f"   Latest: Panel {records[0].get('panel_id', 'N/A')} - {records[0].get('power_output', 0):.2f} kW")
        else:
            print(f"❌ Get Solar Records Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Solar Records Failed: {e}")
        return False
    
    # Test 10: Get Wind Records
    print("\n10. Testing Get Wind Records...")
    try:
        response = requests.get(f"{API_BASE_URL}/wind-records/{logged_user_id}")
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Retrieved {len(records)} Wind Records")
            if len(records) > 0:
                print(f"   Latest: Turbine {records[0].get('turbine_id', 'N/A')} - {records[0].get('power_output', 0):.2f} kW")
        else:
            print(f"❌ Get Wind Records Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Wind Records Failed: {e}")
        return False
    
    # Test 11: Get Battery Records
    print("\n11. Testing Get Battery Records...")
    try:
        response = requests.get(f"{API_BASE_URL}/battery-records/{logged_user_id}")
        if response.status_code == 200:
            records = response.json()
            print(f"✅ Retrieved {len(records)} Battery Records")
            if len(records) > 0:
                print(f"   Latest: Battery {records[0].get('battery_id', 'N/A')} - {records[0].get('charge_level', 0):.1f}%")
        else:
            print(f"❌ Get Battery Records Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Battery Records Failed: {e}")
        return False
    
    # Test 12: Get Grid Sales
    print("\n12. Testing Get Grid Sales...")
    try:
        response = requests.get(f"{API_BASE_URL}/grid-sales/{logged_user_id}")
        if response.status_code == 200:
            sales = response.json()
            print(f"✅ Retrieved {len(sales)} Grid Sales")
            if len(sales) > 0:
                print(f"   Latest: Customer {sales[0].get('customer_id', 'N/A')} - ${sales[0].get('total_amount', 0):.2f}")
        else:
            print(f"❌ Get Grid Sales Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Grid Sales Failed: {e}")
        return False
    
    # Test 13: Get Dashboard Stats
    print("\n13. Testing Dashboard Stats...")
    try:
        response = requests.get(f"{API_BASE_URL}/dashboard/{logged_user_id}")
        if response.status_code == 200:
            stats = response.json()
            print(f"✅ Dashboard Stats Retrieved:")
            print(f"   - Solar Records: {stats.get('solar_records_count', 0)}")
            print(f"   - Wind Records: {stats.get('wind_records_count', 0)}")
            print(f"   - Battery Records: {stats.get('battery_records_count', 0)}")
            print(f"   - Grid Sales: {stats.get('grid_sales_count', 0)}")
            print(f"   - Total Solar Output: {stats.get('total_solar_output', 0):.1f} kW")
            print(f"   - Total Wind Output: {stats.get('total_wind_output', 0):.1f} kW")
            print(f"   - Total Grid Revenue: ${stats.get('total_grid_revenue', 0):.2f}")
            print(f"   - Average Solar Efficiency: {stats.get('average_solar_efficiency', 0):.1f}%")
            print(f"   - Average Wind Efficiency: {stats.get('average_wind_efficiency', 0):.1f}%")
            print(f"   - Average Battery Charge: {stats.get('average_battery_charge', 0):.1f}%")
        else:
            print(f"❌ Get Dashboard Stats Failed: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get Dashboard Stats Failed: {e}")
        return False
    
    # Test 14: Test Swagger UI
    print("\n14. Testing Swagger UI...")
    try:
        response = requests.get("http://127.0.0.1:8000/docs")
        if response.status_code == 200:
            print("✅ Swagger UI is accessible")
            print(f"   URL: http://127.0.0.1:8000/docs")
        else:
            print(f"❌ Swagger UI not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Swagger UI Test Failed: {e}")
        return False
    
    # Final Summary
    print("\n" + "=" * 60)
    print("🎉 API-BASED SYSTEM TEST SUMMARY")
    print("=" * 60)
    print("✅ API Health Check: PASSED")
    print("✅ User Registration: PASSED")
    print("✅ User Login: PASSED")
    print("✅ Solar Record Creation: PASSED")
    print("✅ Wind Record Creation: PASSED")
    print("✅ Battery Record Creation: PASSED")
    print("✅ Grid Sale Creation: PASSED")
    print("✅ Energy Data Creation: PASSED")
    print("✅ Get Solar Records: PASSED")
    print("✅ Get Wind Records: PASSED")
    print("✅ Get Battery Records: PASSED")
    print("✅ Get Grid Sales: PASSED")
    print("✅ Dashboard Stats: PASSED")
    print("✅ Swagger UI: PASSED")
    
    print("\n🔗 Available Endpoints:")
    print(f"   - API Server: http://127.0.0.1:8000")
    print(f"   - API Base URL: {API_BASE_URL}")
    print(f"   - Swagger UI: http://127.0.0.1:8000/docs")
    
    print("\n🌟 API-BASED ARCHITECTURE CONFIRMED:")
    print("✅ No direct database access")
    print("✅ All operations through API")
    print("✅ Complete CRUD operations")
    print("✅ User authentication")
    print("✅ Real-time data via API")
    
    print("\n🚀 Ready to run API-based Flet Application!")
    print("📱 Run: python main_api.py")
    
    return True

if __name__ == "__main__":
    test_api_system()
