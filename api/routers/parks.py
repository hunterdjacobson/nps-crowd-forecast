import asyncio
import re
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from api.services import nps_client

router = APIRouter(prefix="/parks", tags=["Parks"])

def parse_lat_long(lat_long_str: str) -> tuple[float, float]:
    """
    Parses "lat:37.84, long:-119.55" into (37.84, -119.55).
    """
    if not lat_long_str:
        return 0.0, 0.0
    
    try:
        # Simple regex to find numbers after 'lat:' and 'long:'
        lat_match = re.search(r"lat:([-+]?\d*\.?\d+)", lat_long_str)
        lon_match = re.search(r"long:([-+]?\d*\.?\d+)", lat_long_str)
        
        lat = float(lat_match.group(1)) if lat_match else 0.0
        lon = float(lon_match.group(1)) if lon_match else 0.0
        
        return lat, lon
    except (ValueError, AttributeError, IndexError):
        return 0.0, 0.0

@router.get("/")
async def search_parks(
    q: str = Query(..., min_length=2),
    limit: int = 20
) -> List[Dict[str, Any]]:
    """
    Searches for parks and returns summarized results including parsed coordinates.
    """
    raw_parks = await nps_client.search_parks(q, limit)
    
    summarized_parks = []
    for p in raw_parks:
        lat, lon = parse_lat_long(p.get("latLong", ""))
        
        summarized_parks.append({
            "park_code": p.get("parkCode"),
            "full_name": p.get("fullName"),
            "states": p.get("states"),
            "lat": lat,
            "lon": lon,
            "description": p.get("description"),
            "designation": p.get("designation"),
            "url": p.get("url")
        })
    
    return summarized_parks

@router.get("/{park_code}")
async def get_park_details(park_code: str) -> Dict[str, Any]:
    """
    Fetches detailed park information, alerts, and visitor centers concurrently.
    """
    park_task = nps_client.get_park_by_code(park_code)
    alerts_task = nps_client.get_park_alerts(park_code)
    visitor_centers_task = nps_client.get_visitor_centers(park_code)
    
    park, alerts, visitor_centers = await asyncio.gather(
        park_task, alerts_task, visitor_centers_task
    )
    
    if park is None:
        raise HTTPException(status_code=404, detail="Park not found")
        
    return {
        "park": park,
        "alerts": alerts,
        "visitor_centers": visitor_centers
    }
