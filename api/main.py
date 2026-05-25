import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.config import settings
from api.services import nps_client, ml_service
from api.routers import health, parks, forecast

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ON STARTUP
    logger.info("API starting up...")
    if ml_service.model is not None:
        logger.info("ML Model verified and loaded.")
    else:
        logger.warning("ML Model failed to load on startup.")
    
    yield
    
    # ON SHUTDOWN
    logger.info("API shutting down...")
    await nps_client.close()

app = FastAPI(
    title="NPS Crowd Forecast API",
    description="Live NPS conditions and ML crowd-level predictions",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(health.router)
app.include_router(parks.router)
app.include_router(forecast.router)

@app.get("/")
async def root():
    """
    Root endpoint for API discovery.
    """
    return {
        "message": "NPS Crowd Forecast API",
        "docs": "/docs",
        "health": "/health"
    }
