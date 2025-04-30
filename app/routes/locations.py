from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models.base import Localisation
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
@router.get("/")
def get_locations(db: Session = Depends(get_db)):
    """Get all locations."""
    try:
        locations = db.query(Localisation).all()
        if not locations:
            # Retourner au moins une localisation par défaut si aucune n'existe
            return [{
                "id": 1,
                "country": "Non spécifié",
                "region": None,
                "iso_code": "XXX"
            }]
        return locations
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des localisations: {str(e)}")
        return [{
            "id": 1,
            "country": "Non spécifié",
            "region": None,
            "iso_code": "XXX"
        }] 
