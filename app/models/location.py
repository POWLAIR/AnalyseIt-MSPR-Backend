from sqlalchemy import Column, Integer, String

from app.db.base_class import Base

class Location(Base):
    id = Column(Integer, primary_key=True, index=True)
    country = Column(String, nullable=False)
    region = Column(String, nullable=True)
    iso_code = Column(String, nullable=True) 