import re
from datetime import date
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from api.services import nps_client, noaa_client, ml_service

router = APIRouter(prefix="/forecast", tags=["Forecast"])

def parse_lat_long(lat_long_str: str) -> tuple[float, float]:
    """
    Parses "lat:37.84, long:-119.55" into (37.84, -119.55).
    Helper copied from parks router for consistency.
    """
    if not lat_long_str:
        return 0.0, 0.0
    
    try:
        lat_match = re.search(r"lat:([-+]?\d*\.?\d+)", lat_long_str)
        lon_match = re.search(r"long:([-+]?\d*\.?\d+)", lat_long_str)
        
        lat = float(lat_match.group(1)) if lat_match else 0.0
        lon = float(lon_match.group(1)) if lon_match else 0.0
        
        return lat, lon
    except (ValueError, AttributeError, IndexError):
        return 0.0, 0.0

@router.get("/{park_code}")
async def get_crowd_forecast(park_code: str) -> Dict[str, Any]:
    park_code = park_code.lower().strip()
    """
    Orchestrates the crowd forecast by combining NPS, NOAA, and ML model data.
    """
    # 1. Get park details
    park = await nps_client.get_park_by_code(park_code)
    if not park:
        raise HTTPException(status_code=404, detail="Park not found")

    # 2. Parse lat/lon for weather lookup
    lat, lon = parse_lat_long(park.get("latLong", ""))

    # 3. Get weather from NOAA
    weather = await noaa_client.get_weather_forecast(lat, lon)
    
    # 4. Prepare temporal features
    today = date.today()
    month = today.month
    day_of_week = today.weekday()

    # 5. Determine Region
    # LIMITATION: Mapping NPS park addresses to ML regions is complex.
    # Using 'intermountain' as a broad fallback for this prototype.
    # In a production app, we would use a lookup table for all 400+ park codes.
    region = "intermountain"

    # 6. Predict crowd level using ML model
    # Use weather temperature if available, else fallback to 65F
    temp_f = weather.get("temperature")
    if temp_f is None:
        temp_f = 65.0

    crowd_forecast = await ml_service.predict_crowd(
        park_code=park_code,
        month=month,
        day_of_week=day_of_week,
        region=region,
        temperature_f=float(temp_f)
    )

    # 7. Combine and return response
    return {
        "park_code": park_code,
        "park_name": park.get("fullName"),
        "weather": weather,
        "crowd_forecast": crowd_forecast,
        "forecast_date": today.isoformat(),
        "data_sources": [
            "NPS API (Alerts, Park Data)",
            "NOAA API (Weather Forecast)",
            "XGBoost Classifier (Crowd Prediction)"
        ]
    }
