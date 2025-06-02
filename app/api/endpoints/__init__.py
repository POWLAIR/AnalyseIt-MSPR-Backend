# app/api/endpoints/__init__.py

from .admin import router as admin_router
from .auth import router as auth_router
from .dashboard import router as dashboard_router
from .daily_stats import router as daily_stats_router
from .data_sources import router as data_sources_router
from .epidemics import router as epidemics_router
from .location import router as location_router
from .stats import router as stats_router

__all__ = [
    "admin_router",
    "auth_router", 
    "dashboard_router",
    "daily_stats_router",
    "data_sources_router",
    "epidemics_router",
    "location_router",
    "stats_router"
] 