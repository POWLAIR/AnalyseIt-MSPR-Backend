from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models.base import DataSource
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
@router.get("/")
def get_data_sources(db: Session = Depends(get_db)):
    """Get all data sources."""
    try:
        data_sources = db.query(DataSource).all()
        if not data_sources:
            # Retourner au moins une source par défaut si aucune n'existe
            return [{
                "id": 1,
                "source_type": "Manuel",
                "reference": "Données initiales",
                "url": "N/A"
            }]
        return data_sources
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des sources de données: {str(e)}")
        return [{
            "id": 1,
            "source_type": "Manuel",
            "reference": "Données initiales",
            "url": "N/A"
        }] 