import sys
import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

# Add the parent directory to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app
from app.db.session import get_db
from app.db.models.base import Base

# Utiliser SQLite en mémoire par défaut, mais permettre l'override via les variables d'environnement
SQLALCHEMY_DATABASE_URL = os.getenv(
    'SQLALCHEMY_DATABASE_URL',
    'sqlite://'
)

# Créer l'engine en fonction de l'URL
if SQLALCHEMY_DATABASE_URL.startswith('sqlite'):
    test_engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
else:
    test_engine = create_engine(SQLALCHEMY_DATABASE_URL)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Créer les tables une seule fois au niveau du module
Base.metadata.create_all(bind=test_engine)

@pytest.fixture(scope="function")
def db_session():
    connection = test_engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()

@pytest.fixture(scope="function")
def override_get_db(db_session):
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass
    return _override_get_db

@pytest.fixture(scope="function")
def client(override_get_db):
    # Override la dépendance get_db
    app.dependency_overrides[get_db] = override_get_db
    
    # Override l'engine de l'application pour utiliser la base de test
    from app.db import session
    original_engine = session.engine
    session.engine = test_engine
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Restaurer l'engine original après les tests
    session.engine = original_engine
    app.dependency_overrides.clear() 