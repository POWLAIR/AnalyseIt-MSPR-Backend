from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from ..db.session import get_db
from ..db.models.base import Epidemic, DailyStats
from typing import Optional
import logging
from datetime import datetime, timedelta
from pydantic import BaseModel

logger = logging.getLogger(__name__)

router = APIRouter()

class EpidemicCreate(BaseModel):
    name: str
    type: str
    start_date: str
    country: str
    description: str
    source: str
    end_date: Optional[str] = None

class EpidemicUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    start_date: Optional[str] = None
    country: Optional[str] = None
    description: Optional[str] = None
    source: Optional[str] = None
    end_date: Optional[str] = None

@router.post("", status_code=status.HTTP_201_CREATED)
@router.post("/", status_code=status.HTTP_201_CREATED)
def create_epidemic(epidemic: EpidemicCreate, db: Session = Depends(get_db)):
    """
    Crée une nouvelle épidémie.
    """
    try:
        db_epidemic = Epidemic(
            name=epidemic.name,
            type=epidemic.type,
            start_date=datetime.strptime(epidemic.start_date, "%Y-%m-%d"),
            country=epidemic.country,
            description=epidemic.description,
            source=epidemic.source,
            end_date=datetime.strptime(epidemic.end_date, "%Y-%m-%d") if epidemic.end_date else None
        )
        db.add(db_epidemic)
        db.commit()
        db.refresh(db_epidemic)
        return db_epidemic
    except Exception as e:
        logger.error(f"Erreur lors de la création de l'épidémie: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la création de l'épidémie"
        )

@router.patch("/{epidemic_id}")
def update_epidemic(epidemic_id: int, epidemic: EpidemicUpdate, db: Session = Depends(get_db)):
    """
    Met à jour une épidémie existante.
    """
    try:
        db_epidemic = db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
        if not db_epidemic:
            raise HTTPException(
                status_code=404,
                detail="Épidémie non trouvée"
            )

        update_data = epidemic.model_dump(exclude_unset=True)
        
        # Convertir les dates si elles sont présentes
        if "start_date" in update_data:
            update_data["start_date"] = datetime.strptime(update_data["start_date"], "%Y-%m-%d")
        if "end_date" in update_data and update_data["end_date"]:
            update_data["end_date"] = datetime.strptime(update_data["end_date"], "%Y-%m-%d")

        for field, value in update_data.items():
            setattr(db_epidemic, field, value)

        db.commit()
        db.refresh(db_epidemic)
        return db_epidemic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la mise à jour de l'épidémie: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la mise à jour de l'épidémie"
        )

@router.delete("/{epidemic_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_epidemic(epidemic_id: int, db: Session = Depends(get_db)):
    """
    Supprime une épidémie.
    """
    try:
        db_epidemic = db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
        if not db_epidemic:
            raise HTTPException(
                status_code=404,
                detail="Épidémie non trouvée"
            )

        db.delete(db_epidemic)
        db.commit()
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de l'épidémie: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la suppression de l'épidémie"
        )

@router.get("")
@router.get("/")
def get_epidemics(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = None,
    type: Optional[str] = None,
    country: Optional[str] = None,
    sort_by: Optional[str] = "name",
    sort_desc: bool = False
):
    """
    Récupère la liste des épidémies avec pagination et filtrage.
    """
    try:
        # Construire la requête de base
        query = db.query(Epidemic)

        # Appliquer les filtres
        if search:
            search_term = f"%{search}%"
            query = query.filter(
                (Epidemic.name.ilike(search_term))
                | (Epidemic.type.ilike(search_term))
                | (Epidemic.country.ilike(search_term))
            )
        
        if type and type != "all":
            query = query.filter(Epidemic.type == type)
            
        if country and country != "all":
            query = query.filter(Epidemic.country == country)

        # Appliquer le tri
        if sort_by:
            sort_column = getattr(Epidemic, {
                "name": "name",
                "cases": "total_cases",
                "deaths": "total_deaths",
                "date": "start_date"
            }.get(sort_by, "name"))
            
            if sort_desc:
                query = query.order_by(desc(sort_column))
            else:
                query = query.order_by(sort_column)

        # Calculer le nombre total d'éléments
        total = query.count()

        # Appliquer la pagination
        epidemics = query.offset(skip).limit(limit).all()

        # Préparer la réponse
        return {
            "items": epidemics,
            "total": total,
            "page": skip // limit + 1,
            "pages": (total + limit - 1) // limit
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des épidémies: {str(e)}")
        return {
            "items": [],
            "total": 0,
            "page": 1,
            "pages": 1
        }

@router.get("/stats/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """
    Récupère les statistiques agrégées pour le tableau de bord.
    """
    try:
        # Structure de retour par défaut pour données vides
        empty_response = {
            "global_stats": {
                "total_cases": 0,
                "total_deaths": 0,
                "total_epidemics": 0,
                "active_epidemics": 0,
                "mortality_rate": 0
            },
            "type_distribution": [{
                "type": "Non spécifié",
                "cases": 0,
                "deaths": 0
            }],
            "geographic_distribution": [{
                "country": "Non spécifié",
                "cases": 0,
                "deaths": 0
            }],
            "daily_evolution": [{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "new_cases": 0,
                "new_deaths": 0,
                "active_cases": 0
            }],
            "top_active_epidemics": []
        }

        # Vérifier si la table est vide
        has_data = db.query(Epidemic).first() is not None
        if not has_data:
            return empty_response

        # Statistiques globales
        total_stats = db.query(
            func.sum(Epidemic.total_cases).label("total_cases"),
            func.sum(Epidemic.total_deaths).label("total_deaths"),
            func.count(Epidemic.id).label("total_epidemics")
        ).first()

        if not total_stats or total_stats.total_cases is None:
            return empty_response

        # Compter les épidémies actives séparément
        active_epidemics = db.query(func.count(Epidemic.id)).filter(
            Epidemic.end_date.is_(None)
        ).scalar() or 0

        # Tendances par type
        type_stats = db.query(
            Epidemic.type,
            func.sum(Epidemic.total_cases).label("cases"),
            func.sum(Epidemic.total_deaths).label("deaths")
        ).group_by(Epidemic.type).all()

        # Tendances géographiques
        geo_stats = db.query(
            Epidemic.country,
            func.sum(Epidemic.total_cases).label("cases"),
            func.sum(Epidemic.total_deaths).label("deaths")
        ).group_by(Epidemic.country).all()

        # Évolution dans le temps (30 derniers jours)
        thirty_days_ago = datetime.now() - timedelta(days=30)
        daily_evolution = db.query(
            DailyStats.date,
            func.sum(DailyStats.new_cases).label("new_cases"),
            func.sum(DailyStats.new_deaths).label("new_deaths"),
            func.sum(DailyStats.active).label("active_cases")
        ).filter(
            DailyStats.date >= thirty_days_ago
        ).group_by(
            DailyStats.date
        ).order_by(
            DailyStats.date
        ).all()

        # Top 5 des épidémies les plus actives
        top_epidemics = db.query(
            Epidemic
        ).filter(
            Epidemic.end_date.is_(None)
        ).order_by(
            desc(Epidemic.total_cases)
        ).limit(5).all()

        # Calcul du taux de mortalité avec vérification de division par zéro
        total_cases = total_stats.total_cases or 0
        total_deaths = total_stats.total_deaths or 0
        mortality_rate = (total_deaths / total_cases * 100) if total_cases > 0 else 0

        return {
            "global_stats": {
                "total_cases": total_cases,
                "total_deaths": total_deaths,
                "total_epidemics": total_stats.total_epidemics or 0,
                "active_epidemics": active_epidemics,
                "mortality_rate": round(mortality_rate, 2)
            },
            "type_distribution": [
                {
                    "type": stat.type or "Non spécifié",
                    "cases": stat.cases or 0,
                    "deaths": stat.deaths or 0
                } for stat in (type_stats if type_stats else [])
            ] or [{"type": "Non spécifié", "cases": 0, "deaths": 0}],
            "geographic_distribution": [
                {
                    "country": stat.country or "Non spécifié",
                    "cases": stat.cases or 0,
                    "deaths": stat.deaths or 0
                } for stat in (geo_stats if geo_stats else [])
            ] or [{"country": "Non spécifié", "cases": 0, "deaths": 0}],
            "daily_evolution": [
                {
                    "date": stat.date.strftime("%Y-%m-%d"),
                    "new_cases": stat.new_cases or 0,
                    "new_deaths": stat.new_deaths or 0,
                    "active_cases": stat.active_cases or 0
                } for stat in (daily_evolution if daily_evolution else [])
            ] or [{
                "date": datetime.now().strftime("%Y-%m-%d"),
                "new_cases": 0,
                "new_deaths": 0,
                "active_cases": 0
            }],
            "top_active_epidemics": [
                {
                    "id": epidemic.id,
                    "name": epidemic.name,
                    "type": epidemic.type or "Non spécifié",
                    "country": epidemic.country or "Non spécifié",
                    "total_cases": epidemic.total_cases or 0,
                    "total_deaths": epidemic.total_deaths or 0
                } for epidemic in (top_epidemics if top_epidemics else [])
            ]
        }
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des statistiques du tableau de bord: {str(e)}")
        return empty_response

@router.get("/{epidemic_id}")
def get_epidemic(epidemic_id: int, db: Session = Depends(get_db)):
    """
    Récupère les détails d'une épidémie spécifique.
    """
    try:
        epidemic = db.query(Epidemic).filter(Epidemic.id == epidemic_id).first()
        if not epidemic:
            raise HTTPException(
                status_code=404,
                detail="Épidémie non trouvée"
            )
        return epidemic
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de l'épidémie: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Erreur lors de la récupération de l'épidémie"
        ) 