from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import inspect

from .core.config.settings import settings
from .db.session import engine
from .db.models.base import Base
from .routes import stats, epidemics, dashboard, daily_stats, locations, data_sources
from .api.endpoints import admin

# --- optionnel ---
try:
    from .routes import api_technique  # Si jamais on veut séparer api technique plus tard
except ImportError:
    api_technique = None

# Configurer le logger
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    redirect_slashes=False
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Démarrage de l'application ---
@app.on_event("startup")
async def startup_db_client():
    try:
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        required_tables = {"epidemic", "data_source", "localisation", "daily_stats", "overall_stats"}

        if not required_tables.issubset(existing_tables):
            missing_tables = required_tables - existing_tables
            logger.info(f"Tables manquantes: {missing_tables}")
            logger.info("Initialisation des tables de la base de données...")
            Base.metadata.create_all(bind=engine)
            logger.info("Tables initialisées avec succès")
        else:
            logger.info("Toutes les tables requises existent déjà dans la base de données")
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des tables: {str(e)}")

# --- Routing en fonction de la configuration ---

# Base API toujours incluse
app.include_router(
    epidemics.router,
    prefix=f"{settings.API_V1_STR}/epidemics",
    tags=["Épidémies"]
)
app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["Analyse détaillée"]
)
app.include_router(
    stats.router,
    prefix=f"{settings.API_V1_STR}/stats",
    tags=["Statistiques"]
)
app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["Administration"]
)
app.include_router(
    daily_stats.router,
    prefix=f"{settings.API_V1_STR}/daily-stats",
    tags=["Statistiques quotidiennes"]
)
app.include_router(
    locations.router,
    prefix=f"{settings.API_V1_STR}/locations",
    tags=["Localisations"]
)
app.include_router(
    data_sources.router,
    prefix=f"{settings.API_V1_STR}/data-sources",
    tags=["Sources de données"]
)

# Activation conditionnelle selon le pays
if settings.ENABLE_API_TECHNIQUE:
    if api_technique:
        app.include_router(
            api_technique.router,
            prefix=f"{settings.API_V1_STR}/api-tech",
            tags=["API Technique"]
        )
        logger.info("API Technique activée.")
    else:
        logger.warning("API Technique demandée mais module non disponible.")

if settings.ENABLE_DATAVIZ:
    try:
        from .routes import dataviz
        app.include_router(
            dataviz.router,
            prefix=f"{settings.API_V1_STR}/dataviz",
            tags=["Dataviz"]
        )
        logger.info("Module de Dataviz activé.")
    except ImportError:
        logger.warning("Module Dataviz demandé mais non présent.")

# --- Routes de test ---
@app.get("/test-endpoint")
def test_endpoint():
    return {"message": "Le backend fonctionne correctement !"}

@app.get("/test-db")
def test_db():
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        return {"message": "Database connection successful", "tables": tables}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}
