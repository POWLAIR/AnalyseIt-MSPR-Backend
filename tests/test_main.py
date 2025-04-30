import sys
from pathlib import Path

# Ajouter le chemin parent au sys.path pour que Python trouve `main.py`
sys.path.append(str(Path(__file__).resolve().parent.parent))

from app.main import app  # noqa: E402

from fastapi.testclient import TestClient
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import get_db
from app.db.models.base import Base

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture
def test_client():
    """Fixture pour créer un client de test."""
    return TestClient(app)


def test_health_check(test_client):
    """Test de l'endpoint de santé."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_dashboard_overview(test_client):
    """Test de l'endpoint du tableau de bord."""
    response = test_client.get("/api/v1/dashboard/overview")
    assert response.status_code == 200
    data = response.json()
    assert "totalPandemics" in data
    assert "activePandemics" in data
    assert "averageTransmissionRate" in data
    assert "averageMortalityRate" in data
    assert "latestStats" in data
    assert all(key in data["latestStats"] for key in ["cases", "deaths", "recovered", "date"])


def test_dashboard_trends(test_client):
    """Test de l'endpoint des tendances du tableau de bord."""
    response = test_client.get("/api/v1/dashboard/trends")
    assert response.status_code == 200
    data = response.json()
    assert "dailyStats" in data
    assert isinstance(data["dailyStats"], list)


def test_epidemics_list(test_client):
    """Test de l'endpoint de liste des épidémies."""
    response = test_client.get("/api/v1/epidemics")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert isinstance(data["items"], list)


def test_daily_stats_list(test_client):
    """Test de l'endpoint de liste des statistiques quotidiennes."""
    response = test_client.get("/api/v1/daily-stats")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_locations_list(test_client):
    """Test de l'endpoint de liste des localisations."""
    response = test_client.get("/api/v1/locations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_data_sources_list(test_client):
    """Test de l'endpoint de liste des sources de données."""
    response = test_client.get("/api/v1/data-sources")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_etl_data_integrity():
    """Test de l'intégrité des données ETL."""
    from app.services.data_extraction import extract_and_load_datasets
    assert extract_and_load_datasets is not None
