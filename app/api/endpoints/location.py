from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.api.dependencies import get_db_session
from app.api.schemas import Location, LocationCreate, LocationUpdate, Response
from app.db.repositories import location_repository

router = APIRouter()

@router.get("/", response_model=List[Location])
def read_locations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db_session)
):
    """
    Récupère la liste des localisations avec pagination optionnelle.
    """
    return location_repository.get_locations(db, skip=skip, limit=limit)

@router.post("/", response_model=Location)
def create_location(
    location: LocationCreate,
    db: Session = Depends(get_db_session)
):
    """
    Crée une nouvelle localisation.
    """
    return location_repository.create_location(db=db, location=location)

@router.get("/{location_id}", response_model=Location)
def read_location(location_id: int, db: Session = Depends(get_db_session)):
    """
    Récupère une localisation spécifique par son ID.
    """
    db_location = location_repository.get_location(db, location_id=location_id)
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location

@router.put("/{location_id}", response_model=Location)
def update_location(
    location_id: int,
    location: LocationUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Met à jour une localisation existante.
    """
    db_location = location_repository.update_location(
        db, location_id=location_id, location=location
    )
    if db_location is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return db_location

@router.delete("/{location_id}", response_model=Response)
def delete_location(location_id: int, db: Session = Depends(get_db_session)):
    """
    Supprime une localisation par son ID.
    """
    success = location_repository.delete_location(db, location_id=location_id)
    if not success:
        raise HTTPException(status_code=404, detail="Location not found")
    return {"status": "success", "message": "Location deleted successfully"} 
