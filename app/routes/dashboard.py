from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..db.session import get_db
from ..db.models.base import Epidemic, DailyStats
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Récupère les données générales pour l'analyse détaillée.
    """
    try:
        # Statistiques des épidémies
        total_pandemics = db.query(Epidemic).count()
        active_pandemics = db.query(Epidemic).filter(Epidemic.end_date is None).count()

        # Calcul des taux moyens
        latest_stats = db.query(
            func.avg(DailyStats.new_cases * 100.0 / func.nullif(DailyStats.cases, 0)).label('transmission_rate'),
            func.avg(DailyStats.deaths * 100.0 / func.nullif(DailyStats.cases, 0)).label('mortality_rate')
        ).first()

        # Récupération des dernières statistiques
        latest_data = db.query(DailyStats).order_by(DailyStats.date.desc()).first()

        return {
            "totalPandemics": total_pandemics,
            "activePandemics": active_pandemics,
            "averageTransmissionRate": float(latest_stats.transmission_rate or 0),
            "averageMortalityRate": float(latest_stats.mortality_rate or 0),
            "latestStats": {
                "cases": latest_data.cases if latest_data else 0,
                "deaths": latest_data.deaths if latest_data else 0,
                "recovered": latest_data.recovered if latest_data else 0,
                "date": latest_data.date.isoformat() if latest_data else datetime.now().isoformat()
            }
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des données de l'analyse détaillée: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des données de l'analyse détaillée"
        )

@router.get("/trends")
def get_dashboard_trends(db: Session = Depends(get_db)):
    """
    Récupère les tendances pour l'analyse détaillée.
    """
    try:
        # Récupération des statistiques des 7 derniers jours
        recent_stats = db.query(DailyStats)\
            .order_by(DailyStats.date.desc())\
            .limit(7)\
            .all()

        return {
            "dailyStats": [
                {
                    "date": stat.date.isoformat(),
                    "cases": stat.cases,
                    "deaths": stat.deaths,
                    "recovered": stat.recovered
                }
                for stat in recent_stats
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des tendances: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération des tendances"
        ) 