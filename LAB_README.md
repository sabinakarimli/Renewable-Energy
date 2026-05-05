# 🔬 Laboratory Work #9 - FastAPI + SQLite3 + Flet

## 📋 Objective
Extend FastAPI server with POST method connected to SQLite3 database, and implement a record submission form in Flet application with navigation between two windows using NavigationBar.

## 🏗️ Architecture
```
Flet App ↔ FastAPI ↔ SQLite3 Database
   ↓           ↓           ↓
  POST/GET   API Routes   Energy Records
```

## 📁 Files Created
- `lab_api.py` - FastAPI server with SQLite3 integration
- `lab_app.py` - Flet application with NavigationBar
- `lab_startup.py` - Startup script for both services
- `lab_test.py` - Testing script for API endpoints
- `renewable_energy_lab.db` - SQLite3 database (auto-created)

## 🚀 Quick Start

### Option 1: Use Startup Script (Recommended)
```bash
python lab_startup.py
```

### Option 2: Manual Start
**Terminal 1 - Start FastAPI Server:**
```bash
python -m uvicorn lab_api:app --reload --port 8000
```

**Terminal 2 - Start Flet App:**
```bash
python lab_app.py
```

## 🧪 Testing

### Test API Endpoints
```bash
python lab_test.py
```

### Test via Browser
1. Open http://127.0.0.1:8000/docs
2. Test POST `/records` via Swagger UI
3. Test GET `/records` to view all records

## 📊 Database Schema
```sql
CREATE TABLE energy_records (
    id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    power_output TEXT NOT NULL,
    efficiency TEXT NOT NULL
);
```

## 🔧 API Endpoints

### GET /records
- Returns all energy records from database
- **Response:** `{"id": "1", "source_type": "Solar", "power_output": "5.2", "efficiency": "92.5"}`

### POST /records
- Adds new energy record to database
- **Request:** `{"id": "2", "source_type": "Wind", "power_output": "3.1", "efficiency": "88.2"}`
- **Response:** `{"message": "Record added successfully", "record": {...}}`
- **Error:** `{"error": "ID '2' already exists"}`

### GET /
- Health check endpoint
- **Response:** `{"status": "API is running", "database": "renewable_energy_lab.db"}`

## 📱 Flet Application Features

### Navigation
- **Records Tab**: View all energy records in DataTable
- **Add New Tab**: Form to submit new records

### Form Validation
- All fields required
- Duplicate ID checking
- Real-time feedback via SnackBar

### Data Flow
1. User fills form → POST request → FastAPI → SQLite3
2. DataTable refresh → GET request → FastAPI → SQLite3

## ✅ Testing Checklist

1. **FastAPI Server**
   - [ ] Start server with `uvicorn lab_api:app --reload --port 8000`
   - [ ] Visit http://127.0.0.1:8000/docs
   - [ ] Test POST via Swagger UI
   - [ ] Test GET via Swagger UI

2. **Flet Application**
   - [ ] Start app with `python lab_app.py`
   - [ ] Navigate between tabs
   - [ ] Add new record via form
   - [ ] Verify record appears in table
   - [ ] Test empty field validation
   - [ ] Test duplicate ID handling

3. **Integration Testing**
   - [ ] Run `python lab_test.py`
   - [ ] Verify all tests pass
   - [ ] Check data persistence after restart

## 🎯 Learning Outcomes

### FastAPI Skills
- ✅ SQLite3 database integration
- ✅ Pydantic model validation
- ✅ POST method implementation
- ✅ Error handling (duplicate IDs)

### Flet Skills
- ✅ NavigationBar implementation
- ✅ Window switching (visible=True/False)
- ✅ Form validation
- ✅ DataTable population
- ✅ HTTP requests (requests.post/get)
- ✅ SnackBar notifications

### Database Skills
- ✅ SQLite3 connection management
- ✅ CRUD operations
- ✅ Data persistence
- ✅ Constraint handling

## 🐛 Troubleshooting

### Common Issues

**"Cannot connect to API"**
- Ensure FastAPI server is running on port 8000
- Check firewall settings
- Verify API_URL in lab_app.py

**"Database locked"**
- Restart FastAPI server
- Check for other processes using the database

**"Duplicate ID error"**
- Use unique IDs for each record
- Check existing records before adding

**Flet app not updating**
- Call `page.update()` after changes
- Check navigation logic

## 📈 Extensions (Optional)

1. **Enhanced Validation**
   - Numeric validation for power output
   - Range validation for efficiency
   - Source type dropdown

2. **Advanced Features**
   - Edit existing records
   - Delete records
   - Search/filter functionality
   - Data export (CSV/JSON)

3. **UI Improvements**
   - Loading indicators
   - Better error messages
   - Responsive design
   - Dark mode support

## 🏆 Success Criteria

- ✅ FastAPI server with SQLite3 integration
- ✅ POST method working with validation
- ✅ Flet app with NavigationBar
- ✅ Form submission with error handling
- ✅ DataTable displaying records
- ✅ Complete data flow working
- ✅ Persistence after restart
