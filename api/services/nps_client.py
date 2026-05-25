import httpx
import logging
from typing import List, Dict, Any, Optional
from api.config import settings

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shared httpx.AsyncClient with timeout
client = httpx.AsyncClient(timeout=10.0)

async def close() -> None:
    """Closes the shared httpx client."""
    await client.aclose()
    logger.info("NPS API client closed.")

async def search_parks(query: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Searches for parks by query string.
    """
    logger.info(f"Searching parks with query: '{query}', limit: {limit}")
    url = f"{settings.nps_base_url}/parks"
    params = {
        "q": query,
        "limit": limit,
        "api_key": settings.nps_api_key
    }
    
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"Error searching parks: {e}")
        return []

async def get_park_alerts(park_code: str) -> List[Dict[str, Any]]:
    """
    Fetches alerts for a specific park.
    Each alert dict includes: id, title, description, category, url.
    """
    logger.info(f"Fetching alerts for park: {park_code}")
    url = f"{settings.nps_base_url}/alerts"
    params = {
        "parkCode": park_code,
        "api_key": settings.nps_api_key
    }
    
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"Error fetching alerts for {park_code}: {e}")
        return []

async def get_visitor_centers(park_code: str) -> List[Dict[str, Any]]:
    """
    Fetches visitor centers for a specific park.
    Each visitor center dict includes: name, isPassportStampLocation, operatingHours.
    """
    logger.info(f"Fetching visitor centers for park: {park_code}")
    url = f"{settings.nps_base_url}/visitorcenters"
    params = {
        "parkCode": park_code,
        "api_key": settings.nps_api_key
    }
    
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json().get("data", [])
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"Error fetching visitor centers for {park_code}: {e}")
        return []

async def get_park_by_code(park_code: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single park by its 4-letter code.
    """
    logger.info(f"Fetching park details for: {park_code}")
    url = f"{settings.nps_base_url}/parks"
    params = {
        "parkCode": park_code,
        "limit": 1,
        "api_key": settings.nps_api_key
    }
    
    try:
        response = await client.get(url, params=params)
        response.raise_for_status()
        data = response.json().get("data", [])
        return data[0] if data else None
    except (httpx.HTTPStatusError, httpx.RequestError) as e:
        logger.error(f"Error fetching park {park_code}: {e}")
        return None
