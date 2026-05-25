from fastapi import APIRouter
from api.services import ml_service

router = APIRouter(prefix="/health", tags=["Health"])

@router.get("/")
async def health_check():
    """
    Returns the health status of the API and ML model.
    """
    is_model_loaded = ml_service.model is not None
    
    return {
        "status": "ok" if is_model_loaded else "degraded",
        "model": "loaded" if is_model_loaded else "not_found"
    }
