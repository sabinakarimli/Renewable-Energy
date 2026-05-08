# Laboratory Work #9: FastAPI + SQLite3 + Flet Navigation

## Overview

This laboratory work demonstrates a complete client-server architecture using:
- **FastAPI** as the backend server with SQLite3 database
- **Flet** as the frontend client with NavigationBar for window navigation
- **250+ API endpoints** for comprehensive renewable energy management

## Project Structure

```
Renewable Energy/
├── comprehensive_api_server.py   # FastAPI server with 250+ endpoints
├── lab9_client.py                # Flet client with NavigationBar (Lab 9)
├── flet_client.py                # Full-featured Flet client with 9 views
├── renewable_energy_comprehensive.db  # SQLite3 database (created automatically)
└── LAB9_README.md                # This file
```

## Features

### API Server (comprehensive_api_server.py)

**250+ Endpoints across 14 categories:**

1. **Authentication (15 endpoints)**
   - POST `/auth/register` - Register new user
   - POST `/auth/login` - User login
   - GET `/auth/users` - Get all users
   - GET `/auth/users/{user_id}` - Get user by ID
   - PUT `/auth/users/{user_id}` - Update user
   - DELETE `/auth/users/{user_id}` - Delete user
   - GET `/auth/users/by-role/{role}` - Get users by role
   - GET `/auth/users/active` - Get active users
   - GET `/auth/users/inactive` - Get inactive users
   - GET `/auth/users/by-email/{email}` - Get user by email
   - GET `/auth/users/by-name/{name}` - Search users by name
   - GET `/auth/users/by-phone/{phone}` - Get user by phone
   - GET `/auth/users/recent/{days}` - Get recent users
   - GET `/auth/users/summary` - Get user statistics

2. **Energy Records (20 endpoints)**
   - Full CRUD operations
   - Filter by source, status, location, date, efficiency, power, cost, carbon
   - Summary statistics

3. **Solar Records (20 endpoints)**
   - Full CRUD operations
   - Filter by panel, status, type, orientation, efficiency, temperature, irradiance, power
   - High performance and needs-cleaning queries
   - Summary statistics

4. **Wind Records (20 endpoints)**
   - Full CRUD operations
   - Filter by turbine, status, model, direction, speed, efficiency, power
   - High/low wind queries
   - Maintenance tracking
   - Summary statistics

5. **Battery Records (20 endpoints)**
   - Full CRUD operations
   - Filter by battery, status, type, charge, capacity, voltage, temperature, health, cycles
   - Low/high charge queries
   - Maintenance tracking
   - Summary statistics

6. **Grid Sales (20 endpoints)**
   - Full CRUD operations
   - Filter by customer, status, contract, region, customer type, amount, price, energy
   - High value and pending queries
   - Summary statistics

7. **Analytics (20 endpoints)**
   - Full CRUD operations
   - Filter by metric, category, source, unit, trend, confidence, period
   - High value and recent queries
   - Summary statistics

8. **Predictions (20 endpoints)**
   - Full CRUD operations
   - Filter by type, confidence, model, source, date
   - High confidence and upcoming queries
   - Summary statistics

9. **Settings (20 endpoints)**
   - Full CRUD operations
   - Filter by key, value, category, type
   - Encrypted/unencrypted queries
   - Summary statistics

10. **Alerts (5 endpoints)**
    - GET `/alerts` - Get alerts (with unread filter)
    - POST `/alerts` - Create alert
    - PUT `/alerts/{alert_id}/read` - Mark as read
    - DELETE `/alerts/{alert_id}` - Delete alert

11. **Maintenance (5 endpoints)**
    - Full CRUD operations for maintenance records

12. **Weather (5 endpoints)**
    - GET/POST weather data

13. **Dashboard (5 endpoints)**
    - GET `/dashboard/stats` - Get dashboard statistics

14. **Health Check (1 endpoint)**
    - GET `/` - API status and information

### Database Tables

- `users` - User accounts and authentication
- `energy_records` - General energy production data
- `solar_records` - Solar panel data
- `wind_records` - Wind turbine data
- `battery_records` - Battery storage data
- `grid_sales` - Grid energy sales data
- `analytics` - Analytics and metrics
- `predictions` - AI predictions
- `settings` - System settings
- `alerts` - System alerts
- `maintenance_records` - Maintenance tracking
- `weather_data` - Weather information

## Installation

### Prerequisites

```bash
pip install fastapi uvicorn pydantic flet requests
```

### Step 1: Start the API Server

```bash
python comprehensive_api_server.py
```

The server will start at `http://127.0.0.1:8000`

- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **API Base URL**: `http://127.0.0.1:8000`

### Step 2: Start the Flet Client

**Option A - Lab 9 Client (Simple, 2 windows):**
```bash
python lab9_client.py
```

**Option B - Full Client (9 views with NavigationBar):**
```bash
python flet_client.py
```

## Testing the System

### Test Flow (Lab 9)

1. **Open Swagger UI** at `http://127.0.0.1:8000/docs`
2. **Test POST endpoint** via Swagger UI:
   - Expand `POST /solar/records`
   - Click "Try it out"
   - Fill in the JSON body
   - Click "Execute"
3. **Add record via Flet form**:
   - Open the Flet client
   - Click "Add New" in NavigationBar
   - Fill in the form fields
   - Click "Submit Record"
4. **Verify record appears in table**:
   - Click "Records" in NavigationBar
   - The table should show the new record
5. **Test validation**:
   - Try submitting with empty fields → Snackbar error
   - Try submitting duplicate ID → Snackbar error from SQLite
6. **Test persistence**:
   - Restart the app → Data persists (stored in SQLite3)

### API Testing Examples

#### Register a User
```bash
curl -X POST "http://127.0.0.1:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "email": "test@example.com", "password": "password123"}'
```

#### Login
```bash
curl -X POST "http://127.0.0.1:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser", "password": "password123"}'
```

#### Add Solar Record
```bash
curl -X POST "http://127.0.0.1:8000/solar/records" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "solar_001",
    "user_id": "demo_user",
    "panel_id": "PANEL_001",
    "power_output": 250.5,
    "efficiency": 0.18,
    "temperature": 45.2,
    "irradiance": 850.0,
    "status": "active",
    "timestamp": "2026-05-05T12:00:00"
  }'
```

#### Get Solar Records
```bash
curl "http://127.0.0.1:8000/solar/records?user_id=demo_user&limit=10"
```

## Key Concepts Demonstrated

### 1. HTTP POST Method
- Sending data to the server via `requests.post()`
- JSON payload structure
- Response handling

### 2. Pydantic Models
- Input data validation
- Type checking
- Automatic documentation

### 3. SQLite3 Database
- Connection management
- CRUD operations
- Data persistence
- Integrity constraints (unique IDs)

### 4. FastAPI Features
- Automatic API documentation (Swagger UI)
- Request/response validation
- Error handling
- Query parameters

### 5. Flet Navigation
- NavigationBar component
- View switching with `visible=True/False`
- State management
- Event handling

## Troubleshooting

### API Server won't start
- Check if port 8000 is available
- Ensure all dependencies are installed

### Client can't connect to API
- Make sure the API server is running
- Check the API_URL in the client matches the server

### Database errors
- Delete the `.db` file to reset the database
- Check file permissions

## Laboratory Work Checklist

- [x] FastAPI server with SQLite3 database
- [x] POST method for adding records
- [x] Pydantic model for input validation
- [x] GET method for retrieving records
- [x] Flet form with input fields
- [x] NavigationBar with 2 destinations
- [x] Navigation between windows (visible=True/False)
- [x] Form validation (empty fields check)
- [x] Duplicate ID handling
- [x] Snackbar notifications
- [x] Data persistence in SQLite3
- [x] Swagger UI documentation

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Flet Documentation](https://flet.dev/docs/)
- [SQLite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [Pydantic Documentation](https://docs.pydantic.dev/)