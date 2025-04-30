from typing import Dict, Any
from sqlalchemy.orm import Session
from ..db.models.base import Epidemic, DailyStats, Localisation, DataSource

def run_etl(db: Session) -> Dict[str, Any]:
    """
    Exécute le processus ETL complet.
    """
    try:
        # Exemple de traitement ETL simple
        stats = {
            "processed_epidemics": db.query(Epidemic).count(),
            "processed_daily_stats": db.query(DailyStats).count(),
            "processed_locations": db.query(Localisation).count(),
            "processed_sources": db.query(DataSource).count()
        }
        return {"status": "success", "stats": stats}
    except Exception as e:
        return {"status": "error", "message": str(e)} 