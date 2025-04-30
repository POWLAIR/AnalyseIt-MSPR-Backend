from typing import List, Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.location import Location
from app.api.schemas.location import LocationCreate, LocationUpdate

class CRUDLocation(CRUDBase[Location, LocationCreate, LocationUpdate]):
    def get_by_country(self, db: Session, *, country: str) -> Optional[Location]:
        return db.query(self.model).filter(self.model.country == country).first()

    def get_by_iso_code(self, db: Session, *, iso_code: str) -> Optional[Location]:
        return db.query(self.model).filter(self.model.iso_code == iso_code).first()

    def get_multi_by_region(self, db: Session, *, region: str, skip: int = 0, limit: int = 100) -> List[Location]:
        return db.query(self.model).filter(self.model.region == region).offset(skip).limit(limit).all()


location = CRUDLocation(Location) 
