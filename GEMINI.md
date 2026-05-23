# National Parks Crowd Forecast App — Project Context

## What this project is
A full-stack web application that fetches live data from the NPS API
(alerts, closures, visitor centers) and NOAA weather API, then uses
a pre-trained XGBoost model to forecast crowd levels (Low / Moderate
/ High / Very High) for any US National Park. Frontend: React + Vite
with Leaflet.js map. Backend: FastAPI. Deployed to Vercel + Render.

## Tech stack
- Python 3.12
- FastAPI + uvicorn (backend web framework)
- httpx (async HTTP client for NPS and NOAA calls)
- xgboost 2.x (crowd-level classification)
- scikit-learn (preprocessing, evaluation)
- optuna (hyperparameter tuning)
- joblib (model serialization)
- pandas / numpy (data wrangling)
- pydantic-settings (environment variable management)
- React 18 + Vite (frontend)
- Leaflet.js via react-leaflet (interactive map)
- Axios (frontend HTTP client)
- Tailwind CSS (styling)

## API integrations
- NPS API base URL: https://developer.nps.gov/api/v1
  Key env var: NPS_API_KEY
  Used endpoints: /parks, /alerts, /visitorcenters
- NOAA Weather API base URL: https://api.weather.gov
  No key required. Add header: User-Agent: "nps-crowd-app, your@email.com"
  Used endpoints: /points/{lat},{lon} then /gridpoints/{office}/{x},{y}/forecast

## ML model
- Task: multi-class classification (4 crowd levels)
- Labels: Low, Moderate, High, Very High (derived from monthly visitation quartiles)
- Features: month, day_of_week, is_weekend, is_holiday, park_size_acres,
  park_region, avg_temp_f, precipitation_in, days_since_park_opened
- Model: XGBoost XGBClassifier
- Serialized to: api/models/crowd_model.joblib

## Crowd level thresholds (from NPS data quartiles)
- Low:       < 25th percentile of monthly visitors for that park
- Moderate:  25th–50th percentile
- High:      50th–75th percentile
- Very High: > 75th percentile

## Coding rules
- Use type hints on all Python functions
- All file paths use pathlib.Path, never raw strings
- Backend: never expose API keys in responses
- Frontend: all API calls go through src/api/client.js (never inline fetch)
- All async FastAPI routes use async def with await
- Never hardcode lat/lon or park codes — load from NPS API or config
- Print informative progress messages during ML training

## Project structure
nps-crowd-forecast/
├── api/              (FastAPI backend)
├── data/             (raw and processed CSVs)
├── ml/               (training scripts)
├── frontend/         (React + Vite)
├── render.yaml
├── vercel.json
└── GEMINI.md

## What to never do
- Never put NPS_API_KEY in frontend code or commit .env files
- Never use os.path — use pathlib.Path
- Never use requests in FastAPI routes — use httpx async
- Never import sklearn in api/ — only joblib.load() the model
- Never use class components in React — hooks only