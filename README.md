# National Parks Crowd Forecast

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://nps-crowd-forecast.vercel.app)
[![API Status](https://img.shields.io/badge/api-live-blue)](https://nps-crowd-api.onrender.com/health)

A full-stack application that helps travelers avoid the crowds at US National Parks. It combines live data from the **NPS API** (alerts, closures) and **NOAA Weather API** with a custom-trained **XGBoost machine learning model** to predict crowd levels (Low, Moderate, High, Very High) for any park.

---

## Architecture

```text
                                  +-------------------+
                                  |   NPS IRMA Data   |
                                  | (2010-2025 CSVs)  |
                                  +---------+---------+
                                            |
                                  +---------v---------+
                                  |  XGBoost Trainer  |
                                  | (Python/Scikit)   |
                                  +---------+---------+
                                            |
+-------------------+             +---------v---------+             +-------------------+
|   React Frontend  | <---------> |  FastAPI Backend  | <---------> |      NPS API      |
|  (Vite/Leaflet)   |             |  (Python/httpx)   |             | (Live Alerts/Info)|
+-------------------+             +---------+---------+             +-------------------+
                                            |
                                  +---------v---------+
                                  |      NOAA API     |
                                  | (Live Weather)    |
                                  +-------------------+
```

---

## Machine Learning Model

The crowd forecast is powered by an **XGBoost Classifier** trained on historical visitation patterns.

- **Test Accuracy:** `50.69%` (Predicting exact visitation quartiles across 400+ diverse sites)
- **Training Data:** NPS IRMA Monthly Public Use Reports (2010–2025)
- **Park Coverage:** 400 unique National Park Service units
- **Features:** 
  - Temporal: Month (sin/cos encoding), Day of Week, Is Summer, Is Holiday.
  - Spatial: Region (Alaska, Intermountain, Midwest, National Capital, Northeast, Pacific West, Southeast).
  - Environmental: Live temperature from NOAA.

---

## API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | API discovery and documentation links. |
| `GET` | `/health` | API status and ML model verification. |
| `GET` | `/parks/?q={query}` | Search for parks by name or keyword. |
| `GET` | `/parks/{code}` | Detailed park info, live alerts, and visitor centers. |
| `GET` | `/forecast/{code}` | Combined crowd forecast, weather, and park data. |

---

## Local Development

### 1. Prerequisites
- Python 3.12+
- Node.js 18+
- [NPS API Key](https://www.nps.gov/subjects/developer/get-started.htm)

### 2. Backend Setup
```powershell
# Clone the repository
git clone https://github.com/hunterdjacobson/nps-crowd-forecast.git
cd nps-crowd-forecast/api

# Create and activate virtual environment
python -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Create .env file (copy from example)
copy .env.example .env
# Then edit .env and add your NPS_API_KEY

# Start the server (run from repo root)
uvicorn api.main:app --reload --port 8000
```

### 3. Frontend Setup
```powershell
cd ../frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Environment Variables

| Variable | Description | Source |
| :--- | :--- | :--- |
| `NPS_API_KEY` | (Backend) Authentication for NPS API. | NPS Developer Portal |
| `VITE_API_BASE_URL ` | (Frontend) URL of your FastAPI backend. | Local/Render URL |

---

## Known Limitations

- **Cold Starts:** Since the API is hosted on Render's free tier, the first request after inactivity may take 30-50 seconds to spin up.
- **Region Inference:** The model generalizes parks into 8 broad regions. Local micro-climates or hyper-local events might not be fully captured.
- **Same-Region Prediction:** Parks within the same region with similar temporal features (e.g., two parks in the Southeast in July) may receive similar baseline crowd scores before weather adjustment.

---

## Data Source Credits

- **NPS Visitation Data:** [NPS IRMA Portal](https://irma.nps.gov/Stats/)
- **Park Conditions:** [NPS API](https://www.nps.gov/subjects/developer/index.htm)
- **Weather Data:** [NOAA Weather API](https://www.weather.gov/documentation/services-web-api)
