from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..db.session import get_db
from ..db.models.base import DailyStats
import logging
from ..api.schemas import DailyStatsUpdate

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("")
@router.get("/")
def get_daily_stats(db: Session = Depends(get_db)):
    """Get all daily statistics."""
    try:
        daily_stats = db.query(DailyStats).all()
        if not daily_stats:
            return []
        return daily_stats
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques quotidiennes: {str(e)}")
        return []

@router.put("/{stats_id}")
def update_daily_stats(stats_id: int, stats_update: DailyStatsUpdate, db: Session = Depends(get_db)):
    """Update daily statistics."""
    try:
        # Validate that id_epidemic is not None
        if stats_update.id_epidemic is None:
            raise HTTPException(
                status_code=400,
                detail="Le champ id_epidemic est requis"
            )

        db_stats = db.query(DailyStats).filter(DailyStats.id == stats_id).first()
        if not db_stats:
            raise HTTPException(status_code=404, detail="Statistiques non trouvées")

        # Update the fields
        update_data = stats_update.model_dump(exclude_unset=True)
        
        # Additional validation for required fields
        required_fields = ['id_epidemic', 'id_source', 'id_loc', 'date']
        for field in required_fields:
            if field not in update_data or update_data[field] is None:
                raise HTTPException(
                    status_code=400,
                    detail=f"Le champ {field} est requis"
                )

        for field, value in update_data.items():
            setattr(db_stats, field, value)

        try:
            db.commit()
            db.refresh(db_stats)
            return db_stats
        except Exception as e:
            db.rollback()
            logger.error(f"Erreur lors de la mise à jour en base de données: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Erreur lors de la mise à jour en base de données"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour des statistiques quotidiennes: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour des statistiques") 