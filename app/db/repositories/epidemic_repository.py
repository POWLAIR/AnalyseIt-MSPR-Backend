from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from sqlalchemy import desc, func
import logging

from ..models.base import Epidemic, DailyStats, Localisation, OverallStats
from ...api.schemas import (
    EpidemicCreate,
    EpidemicUpdate
)

logger = logging.getLogger(__name__)

def create_epidemic(db: Session, epidemic: EpidemicCreate) -> Epidemic:
    db_epidemic = Epidemic(**epidemic.model_dump())
    db.add(db_epidemic)
    db.commit()
    db.refresh(db_epidemic)
    return db_epidemic

def get_epidemic(db: Session, epidemic_id: int) -> Optional[Epidemic]:
    try:
        return db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'épidémie {epidemic_id}: {str(e)}")
        raise

def get_epidemics(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Epidemic]:
    """
    Récupère la liste des épidémies avec pagination et filtres optionnels.
    """
    try:
        query = db.query(Epidemic)
        
        if filters:
            for key, value in filters.items():
                if hasattr(Epidemic, key) and value is not None:
                    query = query.filter(getattr(Epidemic, key) == value)
        
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des épidémies: {str(e)}")
        raise

def update_epidemic(
    db: Session,
    epidemic_id: int,
    epidemic: EpidemicUpdate
) -> Optional[Epidemic]:
    try:
        db_epidemic = db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
        if db_epidemic:
            for key, value in epidemic.model_dump(exclude_unset=True).items():
                setattr(db_epidemic, key, value)
            db.commit()
            db.refresh(db_epidemic)
        return db_epidemic
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la mise à jour de l'épidémie {epidemic_id}: {str(e)}")
        raise

def delete_epidemic(db: Session, epidemic_id: int) -> bool:
    try:
        db_epidemic = db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
        if db_epidemic:
            db.delete(db_epidemic)
            db.commit()
            return True
        return False
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la suppression de l'épidémie {epidemic_id}: {str(e)}")
        raise

def get_epidemic_daily_stats(db: Session, epidemic_id: int) -> List[DailyStats]:
    """
    Récupère les statistiques quotidiennes d'une épidémie spécifique
    """
    return db.query(DailyStats)\
        .filter(DailyStats.id_epidemic == epidemic_id)\
        .order_by(DailyStats.date)\
        .all()

def get_filter_options(db: Session) -> dict:
    """
    Récupère les options de filtrage (pays et types uniques)
    """
    try:
        # Récupérer tous les pays uniques
        countries_query = db.query(Epidemic.country)\
            .filter(Epidemic.country.isnot(None))\
            .distinct()\
            .order_by(Epidemic.country)
        countries = [country[0] for country in countries_query.all() if country[0]]
        
        # Récupérer tous les types uniques
        types_query = db.query(Epidemic.type)\
            .filter(Epidemic.type.isnot(None))\
            .distinct()\
            .order_by(Epidemic.type)
        types = [type_[0] for type_ in types_query.all() if type_[0]]
        
        # Si aucun résultat n'est trouvé, fournir des valeurs par défaut
        if not countries:
            countries = ["France", "États-Unis", "Chine", "Royaume-Uni", "Japon"]
        
        if not types:
            types = ["Viral", "Bactérien", "Parasitaire", "Fongique"]
        
        return {
            "countries": countries,
            "types": types
        }
    except Exception as e:
        # Log l'erreur mais renvoyer des valeurs par défaut en cas d'erreur
        print(f"Erreur lors de la récupération des options de filtrage: {str(e)}")
        return {
            "countries": ["France", "États-Unis", "Chine", "Royaume-Uni", "Japon"],
            "types": ["Viral", "Bactérien", "Parasitaire", "Fongique"]
        }

def count_epidemics(db: Session) -> int:
    """
    Compte le nombre total d'épidémies
    """
    return db.query(func.count(Epidemic.id)).scalar()

def get_detailed_epidemic_data(db: Session, skip: int = 0, limit: int = 20) -> List[Dict]:
    """
    Récupère des données détaillées sur les épidémies, incluant statistiques quotidiennes,
    informations géographiques et sources de données
    """
    # Récupérer les épidémies de base
    epidemics = db.query(Epidemic).offset(skip).limit(limit).all()
    
    # Préparer le résultat
    result = []
    
    for epidemic in epidemics:
        # Récupérer les statistiques quotidiennes les plus récentes
        latest_stats = db.query(DailyStats)\
            .filter(DailyStats.id_epidemic == epidemic.id)\
            .order_by(desc(DailyStats.date))\
            .limit(30)\
            .all()
        
        # Récupérer les statistiques globales
        overall_stats = db.query(OverallStats)\
            .filter(OverallStats.id_epidemic == epidemic.id)\
            .first()
        
        # Récupérer toutes les locations affectées par cette épidémie
        affected_locations = db.query(Localisation)\
            .join(DailyStats, DailyStats.id_loc == Localisation.id)\
            .filter(DailyStats.id_epidemic == epidemic.id)\
            .distinct()\
            .all()
        
        # Construire l'objet de données détaillées
        epidemic_data = {
            "id": epidemic.id,
            "name": epidemic.name,
            "type": epidemic.type,
            "country": epidemic.country,
            "start_date": epidemic.start_date.isoformat() if epidemic.start_date else None,
            "end_date": epidemic.end_date.isoformat() if epidemic.end_date else None,
            "description": epidemic.description,
            "transmission_rate": epidemic.transmission_rate,
            "mortality_rate": epidemic.mortality_rate,
            "total_cases": epidemic.total_cases,
            "total_deaths": epidemic.total_deaths,
            "active": epidemic.end_date is None,
            
            # Statistiques globales
            "overall_stats": {
                "total_cases": overall_stats.total_cases if overall_stats else 0,
                "total_deaths": overall_stats.total_deaths if overall_stats else 0,
                "fatality_ratio": overall_stats.fatality_ratio if overall_stats else 0.0
            },
            
            # Données quotidiennes
            "daily_stats": [{
                "date": stat.date.isoformat(),
                "cases": stat.cases,
                "active": stat.active,
                "deaths": stat.deaths,
                "recovered": stat.recovered,
                "new_cases": stat.new_cases,
                "new_deaths": stat.new_deaths,
                "new_recovered": stat.new_recovered,
                "location": {
                    "id": stat.location.id,
                    "country": stat.location.country,
                    "region": stat.location.region,
                    "iso_code": stat.location.iso_code
                }
            } for stat in latest_stats],
            
            # Toutes les locations affectées
            "affected_locations": [{
                "id": loc.id,
                "country": loc.country,
                "region": loc.region,
                "iso_code": loc.iso_code
            } for loc in affected_locations]
        }
        
        result.append(epidemic_data)
    
    return result

def get_epidemic_statistics(db: Session) -> Dict[str, Any]:
    """
    Récupère les statistiques globales sur les épidémies.
    """
    try:
        total_epidemics = db.query(func.count(Epidemic.id)).scalar()
        total_cases = db.query(func.sum(Epidemic.total_cases)).scalar() or 0
        total_deaths = db.query(func.sum(Epidemic.total_deaths)).scalar() or 0
        
        # Calculer le taux de mortalité moyen
        mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0
        
        # Récupérer les épidémies les plus meurtrières
        deadliest_epidemics = (
            db.query(Epidemic)
            .order_by(desc(Epidemic.total_deaths))
            .limit(5)
            .all()
        )
        
        return {
            "total_epidemics": total_epidemics,
            "total_cases": total_cases,
            "total_deaths": total_deaths,
            "average_mortality_rate": mortality_rate,
            "deadliest_epidemics": [
                {
                    "id": e.id,
                    "name": e.name,
                    "total_deaths": e.total_deaths,
                    "mortality_rate": (e.total_deaths / e.total_cases * 100) if e.total_cases > 0 else 0
                }
                for e in deadliest_epidemics
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques: {str(e)}")
        raise 
    