# 🌿 Renewable Energy Management System

A comprehensive renewable energy monitoring and management system built with Flet and FastAPI, featuring real-time data visualization, user authentication, and laboratory work demonstrations.

## 🚀 Features

### Core Application
- **User Authentication System** - Login, registration, and password recovery
- **Real-time Dashboard** - Live monitoring of energy systems
- **Multi-source Support** - Solar, Wind, Battery, and Grid systems
- **Advanced Analytics** - Energy consumption and production analytics
- **AI Predictions** - Machine learning-based energy forecasting
- **Reporting System** - Comprehensive energy reports and exports

### Laboratory Work #9
- **Client-Server Architecture** - FastAPI backend with Flet frontend
- **Complete CRUD Operations** - Create, Read, Update, Delete energy records
- **RESTful API** - Full REST API with Swagger documentation
- **In-memory Storage** - Database-free data management for educational purposes

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flet Client   │────│  FastAPI Server │────│  In-Memory DB  │
│   (Frontend)    │    │   (Backend)     │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 📁 Project Structure

```
Renewable-Energy/
├── main.py                 # Main application entry point
├── assets/                 # Static assets and styles
├── components/             # Reusable UI components
│   ├── sidebar.py         # Navigation sidebar
│   └── header.py          # Application header
├── views/                  # Application views/pages
│   ├── dashboard.py        # Main dashboard
│   ├── analytics.py        # Energy analytics
│   ├── solar.py           # Solar system monitoring
│   ├── wind.py            # Wind system monitoring
│   ├── battery.py         # Battery management
│   ├── predictions.py     # AI predictions
│   ├── reports.py         # Reporting system
│   ├── settings.py        # Application settings
│   ├── login.py           # User authentication
│   ├── register.py        # User registration
│   └── lab.py             # Laboratory work #9
├── database/               # Database management
│   └── db.py              # Database operations
├── lab_api_server.py       # FastAPI server for lab work
├── lab_crud_test.py        # CRUD operations testing
└── README.md              # This file
```

## 🛠️ Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup
1. Clone the repository:
```bash
git clone https://github.com/sabinakarimli/Renewable-Energy.git
cd Renewable-Energy
```

2. Install dependencies:
```bash
pip install flet fastapi uvicorn requests
```

3. Run the application:
```bash
python main.py
```

## 🧪 Laboratory Work #9

### Running the Lab Environment

1. **Start FastAPI Server:**
```bash
python -m uvicorn lab_api_server:app --reload --port 8001
```

2. **Access Swagger Documentation:**
```
http://127.0.0.1:8001/docs
```

3. **Run CRUD Tests:**
```bash
python lab_crud_test.py
```

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/records` | Get all energy records |
| GET | `/records/{id}` | Get specific record |
| POST | `/records` | Create new record |
| PUT | `/records/{id}` | Update entire record |
| PATCH | `/records/{id}` | Partial update |
| DELETE | `/records/{id}` | Delete record |

## 📊 Features Overview

### 🔐 Authentication System
- User registration and login
- Password recovery functionality
- Session management
- Protected routes

### 📈 Real-time Monitoring
- Live data updates
- Interactive charts and graphs
- Real-time alerts and notifications
- Performance metrics

### 🤖 AI Integration
- Energy consumption predictions
- Anomaly detection
- Optimization recommendations
- Machine learning models

### 📋 Reporting
- Custom report generation
- Data export capabilities
- Historical analysis
- Performance tracking

## 🎨 UI/UX Features

- **Modern Design** - Clean, intuitive interface
- **Dark Theme** - Easy on the eyes
- **Responsive Layout** - Works on all screen sizes
- **Smooth Animations** - Professional user experience
- **Navigation** - Easy-to-use sidebar navigation

## 🔧 Technical Stack

- **Frontend:** Flet (Python GUI framework)
- **Backend:** FastAPI (Python web framework)
- **API Documentation:** Swagger/OpenAPI
- **Data Storage:** In-memory (Lab) / SQLite3 (Production)
- **Authentication:** Custom session management
- **Real-time:** WebSocket connections
- **Visualization:** Custom SVG charts

## 📚 Educational Value

This project demonstrates:
- Client-server architecture
- RESTful API design
- Real-time data visualization
- User authentication systems
- Database operations
- Modern Python development
- GUI application development

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is for educational purposes. Feel free to use and modify for learning.

## 🙏 Acknowledgments

- Flet framework for the amazing GUI capabilities
- FastAPI for the powerful API framework
- The renewable energy community for inspiration

---

**Built with ❤️ for educational purposes**

## 📞 Contact

For questions or suggestions, please visit the GitHub repository:
https://github.com/sabinakarimli/Renewable-Energy
