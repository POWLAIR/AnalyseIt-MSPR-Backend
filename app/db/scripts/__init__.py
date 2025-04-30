import os
import sys
import logging

# Ajout du répertoire parent au chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.session import engine
from app.db.models.base import Base

# Configurer le logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """
    Initialise la base de données en créant toutes les tables définies dans les modèles
    """
    try:
        # Création des tables via SQLAlchemy ORM
        logger.info("Création des tables via SQLAlchemy ORM...")
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Base de données initialisée avec succès.")
    except Exception as e:
        logger.error(f"❌ Erreur lors de l'initialisation de la base de données : {str(e)}")
        raise


if __name__ == "__main__":
    init_db() 
    