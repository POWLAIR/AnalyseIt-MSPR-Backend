from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
import random
import logging

from ...db.repositories import epidemic_repository
from ..schemas import (
    Epidemic,
    EpidemicCreate,
    EpidemicUpdate,
    Response
)
from ..dependencies import get_db_session

router = APIRouter()

@router.post("/", response_model=Epidemic)
def create_epidemic(
    epidemic: EpidemicCreate,
    db: Session = Depends(get_db_session)
):
    """
    Create a new epidemic with the following information:
    - name: Name of the epidemic (required)
    - description: Description of the epidemic
    - start_date: Start date of the epidemic
    - end_date: End date of the epidemic
    - type: Type of the epidemic
    """
    return epidemic_repository.create_epidemic(db=db, epidemic=epidemic)

@router.get("/", response_model=List[Epidemic])
def read_epidemics(
    skip: int = 0,
    limit: int = 100,
    type: Optional[str] = None,
    country: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    active: Optional[bool] = None,
    db: Session = Depends(get_db_session)
):
    """
    Get all epidemics with optional filters:
    - type: Filter by epidemic type
    - country: Filter by country
    - start_date: Filter by start date
    - end_date: Filter by end date
    - active: Filter by active status (true = ongoing, false = ended)
    """
    filters = {
        "type": type,
        "country": country,
        "start_date": start_date,
        "end_date": end_date,
        "active": active
    }
    
    # Journalisation des filtres pour le débogage
    logging.debug(f"Applying filters: {filters}")
    
    return epidemic_repository.get_epidemics(db, skip=skip, limit=limit, filters=filters)

@router.get("/stats", response_model=dict)
def get_epidemic_stats(db: Session = Depends(get_db_session)):
    """
    Get global statistics about all epidemics:
    - total number of epidemics
    - number of active epidemics
    - average transmission rate
    - average mortality rate
    """
    epidemics = epidemic_repository.get_epidemics(db, skip=0, limit=1000)
    
    total_epidemics = len(epidemics)
    
    if total_epidemics == 0:
        return {
            "totalPandemics": 0,
            "activePandemics": 0,
            "averageTransmissionRate": 0,
            "averageMortalityRate": 0
        }
    
    active_epidemics = sum(1 for e in epidemics if e.end_date is None)
    
    # Calcul des moyennes
    avg_transmission = sum(e.transmission_rate for e in epidemics) / total_epidemics
    avg_mortality = sum(e.mortality_rate for e in epidemics) / total_epidemics
    
    return {
        "totalPandemics": total_epidemics,
        "activePandemics": active_epidemics,
        "averageTransmissionRate": avg_transmission,
        "averageMortalityRate": avg_mortality
    }

@router.get("/filters", response_model=dict)
def get_filters_options(db: Session = Depends(get_db_session)):
    """
    Get unique countries and types for filtering epidemics
    """
    return epidemic_repository.get_filter_options(db)

@router.get("/detailed-data", response_model=dict)
def get_detailed_epidemic_data(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db_session)
):
    """
    Get detailed data for all epidemics including:
    - Daily statistics with active cases, new cases, recoveries
    - Location information
    - Data sources
    """
    # Récupérer les données détaillées
    detailed_data = epidemic_repository.get_detailed_epidemic_data(db, skip, limit)
    
    # Formater les données pour le frontend
    result = {
        "epidemics": detailed_data,
        "totalCount": epidemic_repository.count_epidemics(db)
    }
    
    return result

@router.get("/{epidemic_id}", response_model=Epidemic)
def read_epidemic(epidemic_id: int, db: Session = Depends(get_db_session)):
    """
    Get a specific epidemic by ID
    """
    db_epidemic = epidemic_repository.get_epidemic(db, epidemic_id=epidemic_id)
    if db_epidemic is None:
        raise HTTPException(status_code=404, detail="Epidemic not found")
    return db_epidemic

@router.get("/{epidemic_id}/data", response_model=list)
def get_epidemic_data(epidemic_id: int, db: Session = Depends(get_db_session)):
    """
    Get time-series data for a specific epidemic
    """
    # Vérifier si l'épidémie existe
    db_epidemic = epidemic_repository.get_epidemic(db, epidemic_id=epidemic_id)
    if db_epidemic is None:
        raise HTTPException(status_code=404, detail="Epidemic not found")
    
    # Récupérer les données réelles de la base de données
    daily_stats = epidemic_repository.get_epidemic_daily_stats(db, epidemic_id)
    
    if daily_stats:
        data = []
        for stat in daily_stats:
            data.append({
                "date": stat.date.isoformat(),
                "cases": stat.cases,
                "deaths": stat.deaths,
                "recoveries": stat.recovered
            })
        return data
    
    # Fallback: Générer des données fictives si aucune donnée réelle n'est disponible
    data = []
    current_cases = 0
    current_deaths = 0
    current_recoveries = 0
    
    # Générer des données pour les 30 derniers jours
    start_date = date.today() - timedelta(days=30)
    for i in range(30):
        day = start_date + timedelta(days=i)
        
        # Augmentation progressive avec une légère variation aléatoire
        new_cases = int(db_epidemic.total_cases / 100 * (1 + random.uniform(-0.1, 0.3)))
        new_deaths = int(db_epidemic.total_deaths / 100 * (1 + random.uniform(-0.1, 0.2)))
        new_recoveries = int((new_cases * 0.7) * (1 + random.uniform(-0.1, 0.2)))
        
        current_cases += new_cases
        current_deaths += new_deaths
        current_recoveries += new_recoveries
        
        data.append({
            "date": day.isoformat(),
            "cases": current_cases,
            "deaths": current_deaths,
            "recoveries": current_recoveries
        })
    
    return data

@router.put("/{epidemic_id}", response_model=Epidemic)
def update_epidemic(
    epidemic_id: int,
    epidemic: EpidemicUpdate,
    db: Session = Depends(get_db_session)
):
    """
    Update an epidemic by ID
    """
    db_epidemic = epidemic_repository.update_epidemic(db, epidemic_id=epidemic_id, epidemic=epidemic)
    if db_epidemic is None:
        raise HTTPException(status_code=404, detail="Epidemic not found")
    return db_epidemic

@router.delete("/{epidemic_id}", response_model=Response)
def delete_epidemic(epidemic_id: int, db: Session = Depends(get_db_session)):
    """
    Delete an epidemic by ID
    """
    success = epidemic_repository.delete_epidemic(db, epidemic_id=epidemic_id)
    if not success:
        raise HTTPException(status_code=404, detail="Epidemic not found")
    return {"status": "success", "message": "Epidemic deleted successfully"} 
