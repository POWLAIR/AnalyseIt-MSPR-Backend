from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

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

def test_user_flow():
    # 1. Créer une épidémie
    epidemic_data = {
        "name": "Test Epidemic",
        "type": "VIRAL",
        "start_date": "2024-01-01",
        "country": "Test Country",
        "description": "Test Description",
        "source": "Test Source"
    }
    response = client.post("/api/v1/epidemics", json=epidemic_data)
    assert response.status_code == 201
    created_epidemic = response.json()
    epidemic_id = created_epidemic["id"]

    # 2. Lire l'épidémie créée
    response = client.get(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 200
    assert response.json()["name"] == epidemic_data["name"]

    # 3. Mettre à jour l'épidémie
    update_data = {
        "name": "Updated Epidemic",
        "description": "Updated Description"
    }
    response = client.patch(f"/api/v1/epidemics/{epidemic_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == update_data["name"]

    # 4. Filtrer les épidémies
    response = client.get("/api/v1/epidemics", params={
        "type": "VIRAL",
        "search": "Test"
    })
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert len(data["items"]) > 0

    # 5. Supprimer l'épidémie
    response = client.delete(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 204

    # 6. Vérifier que l'épidémie a été supprimée
    response = client.get(f"/api/v1/epidemics/{epidemic_id}")
    assert response.status_code == 404
