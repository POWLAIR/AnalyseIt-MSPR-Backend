from typing import Optional

from pydantic import BaseModel

# Shared properties
class LocationBase(BaseModel):
    country: str
    region: Optional[str] = None
    iso_code: Optional[str] = None

# Properties to receive on location creation
class LocationCreate(LocationBase):
    pass

# Properties to receive on location update
class LocationUpdate(LocationBase):
    country: Optional[str] = None

# Properties shared by models stored in DB
class LocationInDBBase(LocationBase):
    id: int

    class Config:
        from_attributes = True

# Properties to return to client
class Location(LocationInDBBase):
    pass

# Properties stored in DB
class LocationInDB(LocationInDBBase):
    pass 
