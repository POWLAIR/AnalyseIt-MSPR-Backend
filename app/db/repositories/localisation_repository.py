from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from ..models.localisation import Localisation
import logging

logger = logging.getLogger(__name__)

def get_localisations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    filters: Optional[Dict[str, Any]] = None
) -> List[Localisation]:
    """
    Récupère la liste des localisations avec pagination et filtres optionnels.
    """
    try:
        query = db.query(Localisation)
        
        if filters:
            for key, value in filters.items():
                if hasattr(Localisation, key) and value is not None:
                    query = query.filter(getattr(Localisation, key) == value)
        
        return query.offset(skip).limit(limit).all()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des localisations: {str(e)}")
        raise

def get_localisation(db: Session, localisation_id: int) -> Optional[Localisation]:
    """
    Récupère une localisation par son ID.
    """
    try:
        return db.query(Localisation).filter(Localisation.id == localisation_id).first()
    except Exception as e:
        logger.error(f"Erreur lors de la récupération de la localisation {localisation_id}: {str(e)}")
        raise

def create_localisation(db: Session, localisation_data: Dict[str, Any]) -> Localisation:
    """
    Crée une nouvelle localisation.
    """
    try:
        localisation = Localisation(**localisation_data)
        db.add(localisation)
        db.commit()
        db.refresh(localisation)
        return localisation
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la création de la localisation: {str(e)}")
        raise

def update_localisation(
    db: Session,
    localisation_id: int,
    localisation_data: Dict[str, Any]
) -> Optional[Localisation]:
    """
    Met à jour une localisation existante.
    """
    try:
        localisation = get_localisation(db, localisation_id)
        if localisation is None:
            return None
        
        for key, value in localisation_data.items():
            if hasattr(localisation, key):
                setattr(localisation, key, value)
        
        db.commit()
        db.refresh(localisation)
        return localisation
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la mise à jour de la localisation {localisation_id}: {str(e)}")
        raise

def delete_localisation(db: Session, localisation_id: int) -> bool:
    """
    Supprime une localisation.
    """
    try:
        localisation = get_localisation(db, localisation_id)
        if localisation is None:
            return False
        
        db.delete(localisation)
        db.commit()
        return True
    except Exception as e:
        db.rollback()
        logger.error(f"Erreur lors de la suppression de la localisation {localisation_id}: {str(e)}")
        raise 
    