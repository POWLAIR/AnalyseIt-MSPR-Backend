# Expose les classes directement depuis ce module
# Cela évite l'importation circulaire

# Le reste du code va utiliser ces imports directement
from pydantic import BaseModel, HttpUrl
from typing import Optional
from datetime import date

# Epidemic schemas
class EpidemicBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    type: Optional[str] = None
    country: Optional[str] = None
    transmission_rate: Optional[float] = 0.0
    mortality_rate: Optional[float] = 0.0
    total_cases: Optional[int] = 0
    total_deaths: Optional[int] = 0

class EpidemicCreate(EpidemicBase):
    pass

class EpidemicUpdate(EpidemicBase):
    pass

class Epidemic(EpidemicBase):
    id: int
    
    class Config:
        from_attributes = True

# Localisation schemas
class LocalisationBase(BaseModel):
    country: str
    region: Optional[str] = None
    iso_code: Optional[str] = None

class LocalisationCreate(LocalisationBase):
    pass

class LocalisationUpdate(LocalisationBase):
    pass

class Localisation(LocalisationBase):
    id: int
    
    class Config:
        from_attributes = True

# DataSource schemas
class DataSourceBase(BaseModel):
    source_type: str
    reference: Optional[str] = None
    url: HttpUrl

class DataSourceCreate(DataSourceBase):
    pass

class DataSourceUpdate(DataSourceBase):
    pass

class DataSource(DataSourceBase):
    id: int
    
    class Config:
        from_attributes = True

# DailyStats schemas
class DailyStatsBase(BaseModel):
    id_epidemic: int
    id_source: int
    id_loc: int
    date: date
    cases: Optional[int] = 0
    active: Optional[int] = 0
    deaths: Optional[int] = 0
    recovered: Optional[int] = 0
    new_cases: Optional[int] = 0
    new_deaths: Optional[int] = 0
    new_recovered: Optional[int] = 0

class DailyStatsCreate(DailyStatsBase):
    pass

class DailyStatsUpdate(DailyStatsBase):
    pass

class DailyStats(DailyStatsBase):
    id: int
    
    class Config:
        from_attributes = True

# OverallStats schemas
class OverallStatsBase(BaseModel):
    id_epidemic: int
    total_cases: Optional[int] = 0
    total_deaths: Optional[int] = 0
    fatality_ratio: Optional[float] = 0.0

class OverallStatsCreate(OverallStatsBase):
    pass

class OverallStatsUpdate(OverallStatsBase):
    pass

class OverallStats(OverallStatsBase):
    id: int
    
    class Config:
        from_attributes = True

# Response schemas
class Response(BaseModel):
    status: str
    message: str
    data: Optional[dict] = None 
