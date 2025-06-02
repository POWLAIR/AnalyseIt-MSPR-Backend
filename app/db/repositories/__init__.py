# app/db/repositories/__init__.py

from . import epidemic_repository
from . import localisation_repository

# Alias pour compatibilité
location_repository = localisation_repository 