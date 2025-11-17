# 🍽️ RushRadar

**Predictive Analytics Platform for Restaurant Operations**

RushRadar is a machine learning-powered application that predicts restaurant wait times, forecasts menu item sales, and analyzes overall busyness levels to optimize dining operations and improve customer experience.
Being developed as part of the capstone project or Cumulation of a 20 month project from Atlas School in Tulsa, OK. 

---

## 🎯 Project Goals

RushRadar aims to solve three critical restaurant challenges:

1. **Wait Time Prediction** - Accurately predict customer wait times based on party size, time of day, current occupancy, and historical patterns
2. **Item Sales Forecasting** - Predict which menu items will be popular on given days to optimize inventory and kitchen prep
3. **Busyness Analysis** - Provide real-time and predictive insights into restaurant traffic patterns to improve staffing and operations

---

## 🏗️ Architecture

### Tech Stack
- **Frontend**: React + Vite (deployed on Vercel)
- **Backend**: Python + FastAPI (deployed on Railway/Render)
- **Database**: PostgreSQL (hosted on Neon/Supabase)
- **ML/Analytics**: Pandas, Scikit-learn, NumPy

### Data Pipeline
```
POS System → ETL Scripts → PostgreSQL → FastAPI → React Dashboard
                ↓
           ML Models (predictions)
```

---

## 📊 Key Features

### For Restaurant Managers
- **Live wait time estimates** based on current conditions
- **Hourly busyness heatmaps** to optimize staff scheduling
- **Menu item performance tracking** with sales trends
- **Weather & event impact analysis** on restaurant traffic

### For Data Science
- **Clean, normalized database schema** optimized for time-series analysis
- **ETL pipeline** for processing dirty POS system data
- **Feature engineering** incorporating external factors (weather, holidays, local events)
- **RESTful API endpoints** for model predictions and analytics

---

## 🗄️ Database Schema

The application uses a normalized PostgreSQL schema with five core tables:

| Table | Purpose |
|-------|---------|
| `menu_items` | Menu catalog with pricing and categories |
| `orders` | Order-level data (timestamp, party size, totals) |
| `order_items` | Junction table linking orders to specific items |
| `wait_times` | Historical wait time logs (quoted vs. actual) |
| `external_factors` | Daily weather and local event data |

See `backend/database/schema.sql` for complete table definitions.

---

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Setup database
python scripts/setup_db.py

# Run ETL pipeline
python etl/extract.py
python etl/transform.py
python etl/load.py

# Start API server
uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 👥 Team

- **Backend & Data Pipeline**: Nathan Wilson + Ariel Lopez
- **Frontend Dashboard**: John Wilson + Harrison Gearhart

---

## 📈 Roadmap

- [ ] Phase 1: Database schema design & ETL pipeline
- [ ] Phase 2: FastAPI endpoints for basic CRUD operations
- [ ] Phase 3: React dashboard with live metrics
- [ ] Phase 4: ML model training for wait time prediction
- [ ] Phase 5: Item sales forecasting with seasonal trends
- [ ] Phase 6: Real-time busyness prediction with external factors

---

## 📝 License

This project is being developed as part of the capstone project or Cumulation of a 20 month project from Atlas School in Tulsa, OK.

---

## 🤝 Contributing

This is a team project. Please coordinate with team members before making major architectural changes.

### Branch Strategy
- `main` - Production-ready code
- `dev` - Integration branch
- `feature/*` - Individual feature branches

---

**Built with ❤️ and lots of ☕ by the RushRadar team**