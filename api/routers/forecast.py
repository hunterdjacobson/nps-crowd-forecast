import logging
import re
from datetime import date
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
from api.services import nps_client, noaa_client, ml_service

router = APIRouter(prefix="/forecast", tags=["Forecast"])
logger = logging.getLogger(__name__)

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
    raw_region = park.get("region", "").lower().strip()
    state_code = park.get("addresses", [{}])[0].get("stateCode", "").upper().strip()
    
    # Map NPS region names/codes to normalized model values
    REGION_MAP = {
        "southeast": "southeast", "ser": "southeast",
        "northeast": "northeast", "ner": "northeast",
        "midwest": "midwest", "mwr": "midwest",
        "alaska": "alaska", "akr": "alaska",
        "pacific west": "pacific_west", "pacific_west": "pacific_west", "pwr": "pacific_west",
        "intermountain": "intermountain", "imr": "intermountain",
        "national capital": "national_capital", "national_capital": "national_capital", "ncr": "national_capital",
    }

    STATE_TO_REGION = {
        "AL": "southeast", "AR": "southeast", "FL": "southeast", "GA": "southeast", 
        "KY": "southeast", "LA": "southeast", "MS": "southeast", "NC": "southeast", 
        "SC": "southeast", "TN": "southeast", "VA": "southeast", "VI": "southeast", "PR": "southeast",
        "CT": "northeast", "DE": "northeast", "MA": "northeast", "MD": "northeast", 
        "ME": "northeast", "NH": "northeast", "NJ": "northeast", "NY": "northeast", 
        "PA": "northeast", "RI": "northeast", "VT": "northeast", "WV": "northeast",
        "IA": "midwest", "IL": "midwest", "IN": "midwest", "KS": "midwest", 
        "MI": "midwest", "MN": "midwest", "MO": "midwest", "NE": "midwest", 
        "ND": "midwest", "OH": "midwest", "SD": "midwest", "WI": "midwest",
        "AK": "alaska",
        "CA": "pacific_west", "HI": "pacific_west", "ID": "pacific_west", 
        "NV": "pacific_west", "OR": "pacific_west", "WA": "pacific_west", 
        "GU": "pacific_west", "AS": "pacific_west", "MP": "pacific_west",
        "AZ": "intermountain", "CO": "intermountain", "MT": "intermountain", 
        "NM": "intermountain", "OK": "intermountain", "TX": "intermountain", 
        "UT": "intermountain", "WY": "intermountain",
        "DC": "national_capital"
    }

    region = REGION_MAP.get(raw_region, STATE_TO_REGION.get(state_code, "other"))
    logger.info(f"Park {park_code} (State: {state_code}, NPS Region: {raw_region}) mapped to model region: {region}")

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
