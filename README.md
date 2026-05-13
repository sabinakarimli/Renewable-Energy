<div align="center">
  <img src="https://img.shields.io/badge/Status-Active-00C896?style=for-the-badge&logo=statuspage&logoColor=white"/>
  <img src="https://img.shields.io/badge/Python-3.11+-0EA5E9?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flet-Desktop-00C896?style=for-the-badge&logo=flutter&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-Backend-F59E0B?style=for-the-badge&logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite3-Database-10B981?style=for-the-badge&logo=sqlite&logoColor=white"/>

  <br/><br/>

  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/logo-dark.svg">
    <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/logo-light.svg" width="100" alt="Logo"/>
  </picture>

  <h1>☀️ Renewable Energy Management System</h1>
  <p>
    <strong>Professional Desktop Dashboard</strong> for real-time monitoring, AI-powered forecasting, and comprehensive management of renewable energy assets — solar, wind, battery, and grid.
  </p>

  <br/>

  <a href="#-features">Features</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-api-endpoints">API</a> •
  <a href="#-project-structure">Structure</a> •
  <a href="#-tech-stack">Tech Stack</a>

  <br/><br/>

  <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/demo.gif" width="800" alt="Dashboard Demo"/>
</div>

---

## ✨ Features

<table>
<tr>
<td width="50%" valign="top">

### ⚡ Live Dashboard
- Real-time energy production & consumption monitoring
- Live-updating SVG charts (Daily / Weekly / Monthly views)
- Animated battery charge/discharge visualization
- Energy flow bars (Solar → Battery → Home → Grid)
- Smart alerts with dynamic color coding
- Live Data Records table with auto-scroll
- CSV export with database history

</td>
<td width="50%" valign="top">

### 🤖 AI Predictions
- Next-hour solar, wind, consumption & battery forecasting
- Peak hour detection (6–9 PM)
- Tomorrow outlook with confidence scoring
- Live model statistics (accuracy, confidence, data points)
- Training simulation with progress indicator
- Dynamic notification & alert generation

</td>
</tr>
<tr>
<td width="50%" valign="top">

### ☀️ Solar Analytics
- Interactive solar panel efficiency monitoring
- Real-time irradiance, temperature & power output
- Performance ratio & degradation tracking
- Hourly/daily/monthly energy yield charts
- Inverter status & string monitoring
- Live animation of panel orientation

</td>
<td width="50%" valign="top">

### 🌬️ Wind Analytics
- Turbine RPM & power curve visualization
- Wind speed vs. power scatter plot
- Blade pitch angle & yaw control monitoring
- Gearbox & generator temperature tracking
- Theoretical vs. actual power comparison
- Capacity factor & availability metrics

</td>
</tr>
<tr>
<td width="50%" valign="top">

### 🔋 Battery Management
- State of Charge (SoC) with animated gauge
- Charge/discharge cycle tracking
- Depth of Discharge (DoD) & State of Health (SoH)
- Cycle count & calendar aging estimation
- Temperature monitoring with cooling status
- Round-trip efficiency calculation

</td>
<td width="50%" valign="top">

### 📊 Analytics & Reports
- Full CRUD for analytics records with search
- Summary cards (Total, Avg Value, Records, Categories)
- **Server-side pagination, sorting & filtering**
- CSV export per filtered page
- System health metrics & trend analysis
- Historical data comparison & export

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites
- Python **3.11+**
- Windows / macOS / Linux

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/sabinakarimli/Renewable-Energy.git
cd Renewable-Energy

# 2. Create a virtual environment
python -m venv .venv

# 3. Activate it
# Windows:
.\.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Run the Main Application

```bash
python main.py
```

> **Note:** The main app starts **both** the FastAPI backend (port 8000) and the Flet desktop UI automatically.

### Run Components Separately

```bash
# Backend API server
python comprehensive_api_server.py        # http://127.0.0.1:8000
python comprehensive_api_server.py 8001   # Fallback on port 8001

# Swagger documentation
# Open http://127.0.0.1:8000/docs

# Seed demo data
python seed_activity5.py

# Activity #5 standalone client
python lab9_client.py
```

---

## 🏗️ Architecture

<div align="center">
  <pre style="background: #080f1e; padding: 20px; border-radius: 12px; border: 1px solid #0d2235; color: #F9FAFB; text-align: left; font-size: 13px; line-height: 1.6;">

  ┌──────────────────────────────────────────────────────────────────┐
  │                     🖥️  Flet Desktop App                        │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
  │  │Dashboard │  │  Solar   │  │   Wind   │  │   Analytics    │  │
  │  │  View    │  │  View    │  │  View    │  │    View       │  │
  │  └────┬─────┘  └────┬─────┘  └────┬─────┘  └──────┬─────────┘  │
  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
  │  │Battery   │  │Predictions│ │  Reports │  │  Settings      │  │
  │  │  View    │  │  View    │  │  View    │  │  / Profile     │  │
  │  └──────────┘  └──────────┘  └──────────┘  └────────────────┘  │
  └───────────────────────────┬──────────────────────────────────────┘
                              │ HTTP (requests)
                              ▼
  ┌──────────────────────────────────────────────────────────────────┐
  │                     ⚙️  FastAPI Backend                          │
  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌───────────┐  │
  │  │ /analytics │  │  /solar    │  │  /auth     │  │  /users   │  │
  │  │   CRUD     │  │  records   │  │  login/reg │  │  profile  │  │
  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘  └─────┬─────┘  │
  │        └───────────────┴───────────────┴────────────────┘        │
  │                           │                                      │
  │                    SQLite3 (energy.db)                            │
  └──────────────────────────────────────────────────────────────────┘
  </pre>
</div>

### Flow Diagram

```
LiveData.tick() ──► DashboardRealtimeBus ──► on_live_tick() ──► page.update()
       │                       │                       │
       ▼                       ▼                       ▼
  Random simulation     1s threaded loop         UI ref updates
  (solar, wind,         with listener            (cards, charts,
   consume, grid)       broadcast                flow bars, alerts)
```

---

## 📡 API Endpoints

<table>
<tr><th>Method</th><th>Endpoint</th><th>Description</th></tr>

<tr><td><code>POST</code></td><td><code>/register</code></td><td>User registration</td></tr>
<tr><td><code>POST</code></td><td><code>/login</code></td><td>User authentication</td></tr>
<tr><td><code>GET</code></td><td><code>/users/{id}</code></td><td>Get user profile</td></tr>
<tr><td><code>PUT</code></td><td><code>/users/{id}</code></td><td>Update user profile</td></tr>
<tr><td colspan="3"></td></tr>
<tr><td><code>GET</code></td><td><code>/analytics?user_id=&limit=</code></td><td>List analytics records</td></tr>
<tr><td><code>POST</code></td><td><code>/analytics</code></td><td>Create analytics record</td></tr>
<tr><td><code>PUT</code></td><td><code>/analytics/{id}</code></td><td>Update analytics record</td></tr>
<tr><td><code>DELETE</code></td><td><code>/analytics/{id}</code></td><td>Delete analytics record</td></tr>
<tr><td><code>GET</code></td><td><code>/analytics/by-metric/{name}</code></td><td>Search by metric name</td></tr>
<tr><td colspan="3"></td></tr>
<tr><td><code>GET</code></td><td><code>/solar/records</code></td><td>Server-side paginated solar records</td></tr>
<tr><td><code>POST</code></td><td><code>/solar/records</code></td><td>Create solar record</td></tr>
<tr><td><code>PUT</code></td><td><code>/solar/records/{id}</code></td><td>Update solar record</td></tr>
<tr><td><code>DELETE</code></td><td><code>/solar/records/{id}</code></td><td>Delete solar record</td></tr>
</table>

> 📖 **Swagger**: Open `http://127.0.0.1:8000/docs` for interactive API documentation.

---

## 🧱 Project Structure

```
Renewable Energy/
├── 📁 assets/                    # UI constants, colors, shared styles
│   └── styles.py                 # Color palette & theme tokens
├── 📁 backend/                   # WebSocket server utilities
│   └── ws_server.py
├── 📁 components/                # Reusable Flet UI components
├── 📁 database/                  # SQLite helpers
│   └── db.py                     # insert/get energy data operations
├── 📁 docs/                      # Documentation & activity files
├── 📁 views/                     # Application pages
│   ├── dashboard.py              # Live monitoring dashboard
│   ├── analytics.py              # CRUD analytics + summary cards
│   ├── solar.py                  # Solar panel analysis
│   ├── wind.py                   # Wind turbine analysis
│   ├── battery.py                # Battery management
│   ├── predictions.py            # AI forecasting engine
│   ├── reports.py                # Data reports & export
│   ├── grid_sales.py             # Grid sales tracking
│   ├── solar_advanced.py         # Advanced solar metrics
│   ├── login.py                  # User authentication
│   ├── register.py               # User registration
│   ├── forgot_password.py        # Password recovery
│   ├── profile.py                # User profile settings
│   └── settings.py               # Application settings
├── 📄 main.py                    # Entry point with routing
├── 📄 comprehensive_api_server.py # FastAPI backend (port 8000 / 8001)
├── 📄 lab9_client.py             # Activity #5 standalone client
├── 📄 seed_activity5.py          # Demo data seeding script
├── 📄 test_api_system.py         # API integration tests
└── 📄 requirements.txt           # Python dependencies
```

---

## 💻 Tech Stack

<div align="center">

| Technology | Purpose | Badge |
|-----------|---------|-------|
| **Python 3.11+** | Core language | ![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white) |
| **Flet** | Cross-platform desktop UI | ![Flet](https://img.shields.io/badge/UI-Flet-00C896?logo=flutter&logoColor=white) |
| **FastAPI** | REST API backend | ![FastAPI](https://img.shields.io/badge/API-FastAPI-009688?logo=fastapi&logoColor=white) |
| **SQLite3** | Local database | ![SQLite](https://img.shields.io/badge/DB-SQLite3-003B57?logo=sqlite&logoColor=white) |
| **Uvicorn** | ASGI server | ![Uvicorn](https://img.shields.io/badge/Server-Uvicorn-4B8BBE?logo=uvicorn&logoColor=white) |
| **Pydantic** | Data validation | ![Pydantic](https://img.shields.io/badge/Validate-Pydantic-E92063?logo=pydantic&logoColor=white) |
| **Requests** | HTTP client | ![Requests](https://img.shields.io/badge/HTTP-Requests-FF6F00?logo=&logoColor=white) |
| **SVG** | Inline animated charts | ![SVG](https://img.shields.io/badge/Charts-SVG-FFB13B?logo=svg&logoColor=white) |

</div>

---

## 🎨 Theme & Styling

The application features a **dark professional theme** built around a custom design system:

```python
# Core palette
PRIMARY   = "#00C896"   # Vibrant teal-green
SECONDARY = "#0EA5E9"   # Sky blue
ACCENT    = "#F59E0B"   # Amber gold

# Backgrounds
BG_DARK    = "#040d1a"  # Deep navy
BG_CARD    = "#080f1e"  # Card surface
BG_SIDEBAR = "#040d1a"  # Navigation

# Text
TEXT_PRIMARY   = "#F9FAFB"  # Near white
TEXT_SECONDARY = "#9CA3AF"  # Cool gray
TEXT_MUTED     = "#4B5563"  # Dimmed

# Semantic
SUCCESS = "#10B981"  # Green
WARNING = "#F59E0B"  # Amber
ERROR   = "#EF4444"  # Red
INFO    = "#3B82F6"  # Blue
```

---

## 🧪 Testing

```bash
# Verify all Python files compile correctly
python -m py_compile main.py comprehensive_api_server.py lab9_client.py seed_activity5.py

# Run API tests (start the server first in another terminal)
python comprehensive_api_server.py
python test_api_system.py
```

---

## 📸 Screenshots

| Dashboard | Solar Analytics |
|-----------|----------------|
| <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/dashboard.png" width="400"/> | <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/solar.png" width="400"/> |

| Wind Analytics | Battery Management |
|----------------|-------------------|
| <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/wind.png" width="400"/> | <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/battery.png" width="400"/> |

| AI Predictions | Analytics CRUD |
|----------------|----------------|
| <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/predictions.png" width="400"/> | <img src="https://raw.githubusercontent.com/sabinakarimli/Renewable-Energy/main/assets/screenshots/analytics.png" width="400"/> |

---

## 📄 License

This project is developed for educational and demonstration purposes.

---

<div align="center">
  <br/>
  <sub>Built with ❤️ by <a href="https://github.com/sabinakarimli">Sabina Karimli</a></sub>
  <br/><br/>
  <img src="https://img.shields.io/badge/⭐_Star_this_repo-00C896?style=for-the-badge&logo=github&logoColor=white"/>
  <br/><br/>
  <img src="https://profile-counter.glitch.me/sabinakarimli-Renewable-Energy/count.svg" alt="Visitor Count"/>
</div>
