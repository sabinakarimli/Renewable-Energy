# Renewable Energy Management System

A desktop renewable energy monitoring platform built with **Flet**, **FastAPI**, and **SQLite3**. The project includes a modern dashboard experience, system views for solar, wind, battery and grid data, plus an Activity #5 implementation for server-side pagination, live filtering and safe column sorting.

## Highlights

- Flet desktop UI with dark professional styling
- FastAPI backend with automatic Swagger documentation
- SQLite3 persistence for local records
- Solar records table with server-side pagination
- Live search, sort dropdown, order control and page navigation
- CSV export for the currently filtered page
- Seed script for reliable demo data
- Modular UI folders for views, components, styles and database helpers

## Project Structure

```text
Renewable Energy/
├── assets/                         # Shared colors and UI style constants
├── backend/                        # Optional websocket backend utilities
├── components/                     # Reusable Flet UI components
├── database/                       # Local SQLite helpers used by the dashboard
├── docs/                           # Activity and project documentation
├── views/                          # Main dashboard feature pages
├── comprehensive_api_server.py      # FastAPI + SQLite3 backend
├── lab9_client.py                  # Activity #5 Flet client
├── main.py                         # Main Renewable Energy desktop app
├── seed_activity5.py               # Demo data seeding script
├── test_api_system.py              # API smoke/integration checks
├── requirements.txt
└── README.md
```

## Installation

```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Run The Main Dashboard

```powershell
python main.py
```

## Run Activity #5

Start the FastAPI backend:

```powershell
python comprehensive_api_server.py
```

Open Swagger UI:

```text
http://127.0.0.1:8000/docs
```

Seed demo solar records:

```powershell
python seed_activity5.py
```

Start the Flet client:

```powershell
python lab9_client.py
```

## Activity #5 API

The solar records endpoint supports server-side table controls:

```text
GET /solar/records?user_id=demo_user&limit=10&offset=0&search=active&sort_by=timestamp&order=desc
```

Response shape:

```json
{
  "total": 120,
  "limit": 10,
  "offset": 0,
  "items": []
}
```

Sorting is protected by a whitelist, so unsafe values such as `sort_by=id; DROP TABLE solar_records--` fall back to a safe default.

## Useful Commands

```powershell
python -m py_compile main.py comprehensive_api_server.py lab9_client.py seed_activity5.py
python seed_activity5.py
python comprehensive_api_server.py
python lab9_client.py
```

## Notes

Runtime files such as `.venv/`, `__pycache__/`, SQLite `.db` files and generated CSV exports are intentionally ignored. Use `seed_activity5.py` whenever fresh demo data is needed.
