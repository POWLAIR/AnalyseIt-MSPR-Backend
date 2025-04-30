from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import pytest
from datetime import date

from app.main import app
from app.db.session import get_db
from app.db.models.base import Base

# Configuration de la base de données de test
SQLALCHEMY_DATABASE_URL = "sqlite://"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Création des tables pour les tests
Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# Fixtures
@pytest.fixture
def test_epidemic():
    return {
        "name": "Test Epidemic",
        "description": "Test Description",
        "start_date": str(date.today()),
        "end_date": None,
        "type": "VIRAL",
        "country": "Test Country",
        "source": "Test Source"
    }

@pytest.fixture
def test_location():
    return {
        "country": "Test Country",
        "region": "Test Region",
        "iso_code": "TST"
    }

# Tests
def test_create_epidemic(test_epidemic):
    response = client.post("/api/v1/epidemics", json=test_epidemic)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_epidemic["name"]
    assert "id" in data

def test_read_epidemic(test_epidemic):
    # Create test epidemic
    response = client.post("/api/v1/epidemics", json=test_epidemic)
    epidemic_id = response.json()["id"]
    
    # Read created epidemic
    response = client.get(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_epidemic["name"]

def test_update_epidemic(test_epidemic):
    # Create test epidemic
    response = client.post("/api/v1/epidemics", json=test_epidemic)
    epidemic_id = response.json()["id"]
    
    # Update epidemic
    update_data = {"name": "Updated Epidemic"}
    response = client.patch(f"/api/v1/epidemics/{epidemic_id}", json=update_data)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Epidemic"

def test_delete_epidemic(test_epidemic):
    # Create test epidemic
    response = client.post("/api/v1/epidemics", json=test_epidemic)
    epidemic_id = response.json()["id"]
    
    # Delete epidemic
    response = client.delete(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = client.get(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 404

def test_filter_epidemics(test_epidemic):
    # Create test epidemic
    client.post("/api/v1/epidemics", json=test_epidemic)
    
    # Test filters
    response = client.get("/api/v1/epidemics", params={
        "type": "VIRAL",
        "search": "Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0
    assert data["items"][0]["type"] == "VIRAL"

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"} 
    