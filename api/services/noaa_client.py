import httpx
import logging
from typing import Dict, Any
from api.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared httpx.AsyncClient
client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

async def close_client() -> None:
    """Closes the shared httpx client."""
    await client.aclose()
    logger.info("NOAA API client closed.")

async def get_weather_forecast(lat: float, lon: float) -> Dict[str, Any]:
    """
    Fetches the weather forecast for a specific latitude and longitude using NOAA's two-step process.
    """
    headers = {"User-Agent": settings.noaa_user_agent}
    
    try:
        # Step 1: Get grid points from lat/lon
        points_url = f"{settings.noaa_base_url}/points/{lat},{lon}"
        logger.info(f"Fetching NOAA grid points for: {lat}, {lon}")
        
        response = await client.get(points_url, headers=headers)
        
        if response.status_code != 200:
            logger.warning(f"NOAA grid not found for {lat}, {lon} (Status: {response.status_code})")
            return {
                "available": False, 
                "error": "NOAA grid not available for this location"
            }
        
        points_data = response.json()
        properties = points_data.get("properties", {})
        
        grid_id = properties.get("gridId")
        grid_x = properties.get("gridX")
        grid_y = properties.get("gridY")
        
        if not all([grid_id, grid_x, grid_y]):
            return {
                "available": False, 
                "error": "Incomplete NOAA grid metadata for this location"
            }

        # Step 2: Get forecast from grid points
        forecast_url = f"{settings.noaa_base_url}/gridpoints/{grid_id}/{grid_x},{grid_y}/forecast"
        logger.info(f"Fetching NOAA forecast for grid: {grid_id}/{grid_x},{grid_y}")
        
        forecast_response = await client.get(forecast_url, headers=headers)
        forecast_response.raise_for_status()
        
        forecast_data = forecast_response.json()
        periods = forecast_data.get("properties", {}).get("periods", [])
        
        if not periods:
            return {
                "available": False, 
                "error": "No forecast periods available from NOAA"
            }
            
        first_period = periods[0]
        if first_period.get("temperature") is None:
            for i, period in enumerate(periods[1:], start=1):
                if period.get("temperature") is not None:
                    logger.warning(f"First NOAA period has null temperature, using period {i} instead")
                    first_period = period
                    break
        
        prob = first_period.get("probabilityOfPrecipitation", {})
        return {
            "available": True,
            "temperature": first_period.get("temperature"),
            "temperature_unit": first_period.get("temperatureUnit"),
            "precipitation_chance": prob.get("value") if isinstance(prob, dict) else None,
            "wind_speed": first_period.get("windSpeed"),
            "wind_direction": first_period.get("windDirection"),
            "short_forecast": first_period.get("shortForecast"),
            "detailed_forecast": first_period.get("detailedForecast"),
            "forecast_period_name": first_period.get("name")
        }
        
    except Exception as e:
        logger.error(f"Error fetching NOAA forecast for {lat}, {lon}: {e}")
        return {
            "available": False, 
            "error": str(e)
        }
