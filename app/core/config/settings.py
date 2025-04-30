from pydantic_settings import BaseSettings
import os

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Pandemic Data API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "API for tracking and analyzing pandemic data"

    # Database Configuration
    DATABASE_URL: str | None = None
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "password")
    DB_HOST: str = os.getenv("DB_HOST", "mysql_db")
    DB_PORT: str = os.getenv("DB_PORT", "3306")
    DB_NAME: str = os.getenv("DB_NAME", "pandemics_db")

    # CORS
    BACKEND_CORS_ORIGINS: list = ["*"]

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # --- Nouveaux paramètres ajoutés ici ---
    COUNTRY: str = os.getenv("COUNTRY", "fr")  # us, fr, ch
    ENABLE_API_TECHNIQUE: bool = os.getenv("ENABLE_API_TECHNIQUE", "false").lower() == "true"
    ENABLE_DATAVIZ: bool = os.getenv("ENABLE_DATAVIZ", "false").lower() == "true"
    # ---------------------------------------

    @property
    def SQLALCHEMY_DATABASE_URL(self) -> str:
        """Construit l'URL finale pour SQLAlchemy."""
        if self.DATABASE_URL:
            return self.DATABASE_URL
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        case_sensitive = True


# Charger la config
settings = Settings()
