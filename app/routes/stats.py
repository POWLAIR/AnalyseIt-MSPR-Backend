from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..services.stats_service import StatsService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Récupère toutes les statistiques pour le tableau de bord
    """
    try:
        stats_service = StatsService(db)
        return stats_service.get_dashboard_stats()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques du tableau de bord: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des statistiques du tableau de bord"
        ) 