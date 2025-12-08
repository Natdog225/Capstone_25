# DineMetra API

## Forecast. Prepare. Perform.

Real-time restaurant analytics and prediction platform powered by machine learning.

### Description

DineMetra is a comprehensive ML-driven platform that helps restaurant managers optimize operations through intelligent predictions of wait times, busyness levels, and sales. The system integrates real-time data from weather.gov, Ticketmaster events, historical sales, and geolocation to deliver actionable insights.

**In simpler terms:** A web app for restaurant managers that predicts how busy a restaurant will be depending on factors such as past sales data, weather, and other events in the area.

**Key Features:**

- **ML Predictions**: Wait times, busyness, and sales forecasting with confidence intervals
- **Historical Analytics**: Multi-period comparisons (today vs. last week vs. last year)
- **Smart Alerting**: Proactive notifications for critical operational thresholds
- **A/B Testing Framework**: Experiment with model versions and track performance
- **Continuous Learning**: Feedback loop for model retraining and improvement
- **Real-time Data**: Live ingestion via CSV uploads with immediate processing

---

## Quick Start

### Prerequisites

- **Backend**: Python 3.9+, PostgreSQL 13+, FastAPI, MLflow (for model tracking)
- **Frontend**: Node.js 18+, npm 9+, Next.js 14, Vite

### Database Setup

```bash
# Current database setup
psql -U your_username -d dinemetra_db -f backend/database/schema.sql

# Legacy database name (for historical reference)
# psql -U your_username -d rushradar_db -f backend/database/schema.sql
```

### Environment Configuration

```bash
# Backend
cp .env.example .env
# Edit .env with your credentials:
# DATABASE_URL=postgresql://user:pass@localhost/dinemetra_db
# WEATHER_API_KEY=your_weather_gov_key
# TICKETMASTER_API_KEY=your_ticketmaster_key

# Frontend (in /frontend directory)
cp .env.local.example .env.local
# Set NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Install & Run

```bash
# Backend API
pip install -r requirements.txt
cd backend
uvicorn main:app --reload

# Frontend (in a new terminal)
cd frontend
npm install
npm run dev
```

Access the API documentation at: `https://dinemetra-production.up.railway.app/docs#/`

The frontend will be available at: `https://dinemetra.com/`

---

## System Architecture

### Data Flow (Current v2.0)

```mermaid
flowchart TB
    subgraph "Data Sources"
        SALES[Sales CSV Upload<br/>/api/upload/upload-csv]
        WEATHER[Weather.gov API<br/>Real-time Conditions]
        EVENTS[Ticketmaster API<br/>Local Events]
        LABOR[Labor Data<br/>Staffing Levels]
        GEO[Geolocation Data<br/>Restaurant Location]
    end

    subgraph "Data Layer"
        DB[(PostgreSQL<br/>dinemetra_db)]
        CACHE[(Redis Cache<br/>Prediction Cache)]
    end

    subgraph "ML Engine"
        TRAIN[Model Training Pipeline]
        PRED[Prediction Engine<br/>Scikit-Learn / TensorFlow]
        ENH[Enhanced Analysis<br/>Factor Breakdown]
    end

    subgraph "API Services (FastAPI)"
        LEGACY[Legacy API<br/>DEPRECATED - v1.0]
        CURRENT[Current API<br/>v2.0 - /api/predictions/*]
        DASH[Dashboard API<br/>/api/dashboard/*]
        HIST[Historical API<br/>/api/historical/*]
        ALERT[Alert Service<br/>/api/alerts/*]
        EXP[Experiment Service<br/>/api/experiments/*]
    end

    subgraph "Frontend (Next.js + Vite)"
        LOGIN[Login Page<br/>/login]
        DASHBOARD[Manager Dashboard<br/>/dashboard<br/>Real-time Metrics]
        CALENDAR[Calendar View<br/>/calendar<br/>Predictions Timeline]
        ANALYTICS[Analytics Suite<br/>/analytics<br/>Trends & Insights]
    end

    SALES --> DB
    WEATHER --> DB
    EVENTS --> DB
    LABOR --> DB
    GEO --> DB
    
    DB --> TRAIN
    TRAIN --> PRED
    DB --> PRED
    PRED --> ENH
    
    PRED --> LEGACY
    ENH --> CURRENT
    
    DB --> DASH
    PRED --> DASH
    DB --> HIST
    PRED --> ALERT
    PRED --> EXP
    
    CURRENT --> DASHBOARD
    DASH --> DASHBOARD
    HIST --> ANALYTICS
    ALERT --> DASHBOARD
    EXP --> ANALYTICS
    
    DASHBOARD --> CALENDAR
    LOGIN --> DASHBOARD
    
    style LEGACY fill:#ec5a5a,stroke:#cc0000
    style CURRENT fill:#ccffcc,stroke:#00aa00
```

### Key Components

1. **Frontend**: Next.js 14 with TypeScript, styled using Tailwind CSS, built with Vite for optimized development
2. **Prediction Engine**: Dual-mode operation - standard and enhanced (with explainability factors)
3. **Feedback Loop**: Manager-submitted feedback automatically triggers model retraining
4. **Alert Rules Engine**: Configurable thresholds for wait times, busyness, and sales
5. **Model Registry**: MLflow integration for version tracking and A/B testing

---

## API Overview

The API is organized around REST principles with predictable resource URLs.

### Base URL

```
https://dinemetra-production.up.railway.app/
```

### Authentication

API keys are passed via the `X-API-Key` header. Obtain your key from the dashboard.

### Endpoints Structure

| Category | Endpoint Pattern | Description |
|----------|------------------|-------------|
| **Dashboard** | `/api/dashboard/*` | Unified analytics interface |
| **Predictions** | `/api/predictions/{type}` | ML predictions (POST) |
| **Historical** | `/api/historical/compare/*` | Period-over-period analysis |
| **Alerts** | `/api/alerts/*` | Real-time monitoring & notifications |
| **Upload** | `/api/upload/*` | Data ingestion pipeline |
| **Experiments** | `/api/experiments/*` | A/B testing & model comparison |
| **Monitoring** | `/api/monitoring/*` | System health & performance |
| **Legacy** | `/*` | ⚠️ Deprecated endpoints (remove by Q2 2026) |

---

### Frontend Development

The frontend is built with **Next.js 14** and **Vite**, providing:

- **Hot Module Replacement** for instant updates during development
- **Optimized builds** with tree-shaking and code splitting
- **TypeScript support** for type-safe development
- **API Routes** for any server-side rendering needs

**Key Frontend Directories:**
```
frontend/
├── app/                 # Next.js 13+ app router
├── components/          # Reusable React components
├── lib/                 # API client utilities
└── public/              # Static assets
```

---

## Example Usage

### Predict Wait Time with Factor Analysis

```python
import requests
import json

# POST request to enhanced wait time prediction
response = requests.post(
    "https://dinemetra-production.up.railway.app/api/predictions/wait-time-enhanced",
    json={
        "party_size": 4,
        "current_occupancy": 75.5,
        "timestamp": "2025-12-09T19:00:00Z",
        "test_weather_condition": "sunny"  # Optional but useful
    }
)

# Parse the response
if response.status_code == 200:
    data = response.json()
    print(f"Predicted wait: {data['predicted_wait_minutes']} minutes")
    print(f"Confidence: {data['confidence']}")
    print(f"Factors: {json.dumps(data['factors'], indent=2)}")
elif response.status_code == 422:
    print("Validation error:", response.json())
else:
    print(f"Error {response.status_code}: {response.text}")

# Returns: predicted wait, confidence, and factor breakdown
{
  "predicted_wait_minutes": 23,
  "confidence": 0.89,
  "factors": {
    "weather_impact": -2,
    "event_nearby_impact": 7,
    "historical_pattern": 18,
    "occupancy_factor": 15,
    "time_factor": 8
  }
}
```

### Submit Feedback for Model Improvement

```python
requests.post(
    "https://dinemetra-production.up.railway.app/api/dashboard/feedback",
    headers={"X-API-Key": "your_key"},
    json={
        "prediction_type": "wait_time",
        "prediction_id": "pred_12345",
        "actual_value": 28,
        "notes": "Local concert extended intermission"
    }
)
```

---

## Model Versions & A/B Testing

### Current Production Models

- `wait_time_v2.1` - Weather + event-aware wait prediction
- `busyness_v1.8` - Neural network ensemble
- `sales_v3.0` - Prophet + XGBoost hybrid

### Running Experiments

```bash
# Create experiment
curl -X POST https://dinemetra-production.up.railway.app/api/experiments/experiments/create \
  -H "X-API-Key: your_key" \
  -d '{
    "name": "Wait Time Model V3 Test",
    "model_a_version": "wait_time_v2.1",
    "model_b_version": "wait_time_v3.0",
    "prediction_type": "wait_time",
    "duration_days": 14
  }'
```

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created (for experiments/alerts) |
| 400 | Bad Request |
| 401 | Unauthorized (invalid API key) |
| 403 | Forbidden (insufficient permissions) |
| 422 | Validation Error (see `detail` field) |
| 429 | Rate Limit Exceeded |
| 500 | Internal Server Error |

---

## Rate Limiting

- **Prediction endpoints**: 100 requests/minute per API key
- **Dashboard queries**: 1000 requests/minute
- **Data upload**: 10 files/hour (contact support for increase)

---

## Monitoring & Support

### Health Checks

```bash
# System health
curl https://dinemetra-production.up.railway.app/api/monitoring/health

# Model performance metrics
curl https://dinemetra-production.up.railway.app/api/monitoring/model-performance
```

### Support

- **Documentation**: https://docs.dinemetra.com
- **API Status**: Displayed in bottom right corner of the page.

---

## Development Roadmap

### Q1 2026

- [ ] Deprecate legacy endpoints (`/wait-time`, `/busyness`, etc.)
- [ ] Introduce GraphQL endpoint for dashboard queries
- [ ] Add batch prediction endpoint

### Q2 2026

- [ ] Multi-location support
- [ ] Staffing optimization recommendations
- [ ] Mobile app SDK release
- [ ] Deploy frontend to Vercel with CI/CD pipeline

---

## Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Frontend Development Workflow

```bash
# Install dependencies
cd frontend && npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run tests
npm run test
```

---

## License

This API is proprietary software licensed to DineMetra customers. See `LICENSE.md` for details.

---

**Version**: 2.0.0  
**Last Updated**: December 2025  
**API Spec**: [OpenAPI 3.1.0](openapi.json)

## Authors

- **Nathan Wilson**: Project Lead and Machine Learning Engineer  
  [GitHub: @natdog225](https://github.com/natdog225)

- **John Wilson**: Front End Developer and Dashboard Co-creator  
  [GitHub: @Paintballskaguy](https://github.com/Paintballskaguy)

- **Harrison Gearhart**: Front End Developer and Dashboard Co-creator  
  [GitHub: @harrisongearhart](https://github.com/HarrisonGearhart)

- **Ariel Lopez**: API Engineer and Documentation  
  [GitHub: @NecroKnightMare](https://github.com/NecroKnightMare)
  
