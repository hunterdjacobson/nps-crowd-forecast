from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache

class Settings(BaseSettings):
    nps_api_key: str
    app_env: str = "development"
    allowed_origins: str = "http://localhost:5173"
    nps_base_url: str = "https://developer.nps.gov/api/v1"
    noaa_base_url: str = "https://api.weather.gov"
    noaa_user_agent: str = "nps-crowd-app, user@example.com"
    model_path: str = "api/models/crowd_model.joblib"
    encoder_path: str = "api/models/label_encoder.joblib"
    thresholds_path: str = "data/processed/park_thresholds.csv"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=False,
        protected_namespaces=()
    )

    @property
    def origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(",")]

@lru_cache
def get_settings():
    return Settings()

settings = get_settings()
