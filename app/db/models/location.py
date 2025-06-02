from sqlalchemy import Column, Integer, String

from .base import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String(100), nullable=False)
    region = Column(String(150), nullable=True)
    iso_code = Column(String(10), nullable=True) 