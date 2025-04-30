from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query 
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
import logging
from ...db.session import engine
from ...db.models.base import Base
from ..dependencies import get_db_session
from ...services.data_extraction import extract_and_load_datasets
from ...db.session import get_db

# Configurer le logger
logger = logging.getLogger(__name__)

router = APIRouter()

def drop_tables():
    """Supprime toutes les tables existantes en tenant compte des contraintes de clé étrangère."""
    try:
        inspector = inspect(engine)
        
        with engine.begin() as conn:
            # Désactiver temporairement les contraintes de clé étrangère
            conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
            
            # Supprimer les tables dans l'ordre inverse de leur dépendance
            for table_name in inspector.get_table_names():
                logger.info(f"Suppression de la table {table_name}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name}"))
            
            # Réactiver les contraintes de clé étrangère
            conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        
        logger.info("Toutes les tables ont été supprimées avec succès")
    except Exception as e:
        logger.error(f"Erreur lors de la suppression des tables: {str(e)}")
        raise

@router.post("/init-db", response_model=dict)
async def initialize_database(
    background_tasks: BackgroundTasks, 
    reset: bool = Query(False, description="Si true, réinitialise complètement la base de données"),
    db: Session = Depends(get_db_session)
):
    """
    Initialise la base de données avec les tables nécessaires.
    Si reset=true, supprime et recrée toutes les tables.
    """
    try:
        if reset:
            logger.info("Réinitialisation complète de la base de données...")
            drop_tables()
        
        # Création des tables dans la base de données
        logger.info("Création des tables...")
        Base.metadata.create_all(bind=engine)
        logger.info("Tables créées avec succès")
        
        return {
            "success": True,
            "message": "Base de données initialisée avec succès!",
            "reset": reset
        }
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation de la base de données: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors de l'initialisation de la base de données: {str(e)}"
        )

@router.get("/extract-data")
async def extract_data():
    """
    Endpoint pour extraire les données des sources externes.
    """
    try:
        db = next(get_db())
        try:
            result = extract_and_load_datasets(db)
            return {"status": "success", "message": "Data extraction completed", "details": result}
        finally:
            db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/run-etl", response_model=dict)
async def run_etl(
    background_tasks: BackgroundTasks, 
    reset: bool = Query(False, description="Si true, supprime les données existantes avant d'en charger de nouvelles"),
    db: Session = Depends(get_db_session)
):
    """
    Lance le processus ETL pour charger les données.
    Si reset=true, supprime les données existantes avant d'en charger de nouvelles.
    """
    try:
        # Suppression des données existantes si demandé
        if reset:
            logger.info("Suppression des données existantes...")
            from ...db.repositories import epidemic_repository
            # Supprimer toutes les épidémies existantes
            epidemics = epidemic_repository.get_epidemics(db, skip=0, limit=1000)
            for epidemic in epidemics:
                epidemic_repository.delete_epidemic(db, epidemic_id=epidemic.id)
            logger.info("Données existantes supprimées avec succès")

        # Extraire et charger les données depuis Kaggle
        logger.info("Extraction et chargement des données depuis Kaggle...")
        result = extract_and_load_datasets(db)
        logger.info("Données chargées avec succès")

        return {
            "success": True,
            "message": "Données chargées avec succès! Processus ETL complété.",
            "reset": reset,
            "details": result
        }
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Erreur lors du chargement des données: {str(e)}"
        )
