from typing import Generator
from sqlalchemy.orm import Session
from app.db.session import engine

def get_db_session() -> Generator[Session, None, None]:
    """
    Dépendance pour obtenir une session de base de données.
    La session est automatiquement fermée à la fin de la requête.
    """
    session = Session(engine)
    try:
        yield session
    finally:
        session.close() 
