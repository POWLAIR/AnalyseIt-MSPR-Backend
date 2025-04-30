from sqlalchemy import Column, Integer, String, Text, Date, Float, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Epidemic(Base):
    __tablename__ = "epidemic"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    start_date = Column(Date)
    end_date = Column(Date)
    type = Column(String(100))
    country = Column(String(100))
    source = Column(String(255))
    transmission_rate = Column(Float, default=0.0)
    mortality_rate = Column(Float, default=0.0)
    total_cases = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    
    daily_stats = relationship("DailyStats", back_populates="epidemic")
    overall_stats = relationship("OverallStats", back_populates="epidemic")

class Localisation(Base):
    __tablename__ = "localisation"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    country = Column(String(100), nullable=False)
    region = Column(String(150))
    iso_code = Column(String(10), unique=True)
    
    daily_stats = relationship("DailyStats", back_populates="location")

class DataSource(Base):
    __tablename__ = "data_source"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_type = Column(String(100), nullable=False)
    reference = Column(String(255))
    url = Column(String(500), nullable=False)
    
    daily_stats = relationship("DailyStats", back_populates="source")
    
    __table_args__ = (Index('idx_source_type', source_type),)

class DailyStats(Base):
    __tablename__ = "daily_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_epidemic = Column(Integer, ForeignKey('epidemic.id', ondelete='CASCADE', name='fk_daily_stats_epidemic'), nullable=False)
    id_source = Column(Integer, ForeignKey('data_source.id', ondelete='CASCADE', name='fk_daily_stats_source'), nullable=False)
    id_loc = Column(Integer, ForeignKey('localisation.id', ondelete='CASCADE', name='fk_daily_stats_loc'), nullable=False)
    date = Column(Date, nullable=False)
    cases = Column(Integer, default=0)
    active = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    recovered = Column(Integer, default=0)
    new_cases = Column(Integer, default=0)
    new_deaths = Column(Integer, default=0)
    new_recovered = Column(Integer, default=0)
    
    epidemic = relationship("Epidemic", back_populates="daily_stats")
    source = relationship("DataSource", back_populates="daily_stats")
    location = relationship("Localisation", back_populates="daily_stats")
    
    __table_args__ = (
        Index('idx_unique_daily', id_epidemic, id_loc, date, unique=True),
        Index('idx_daily_epidemic', id_epidemic),
        Index('idx_daily_loc', id_loc),
        Index('idx_daily_date', date)
    )

class OverallStats(Base):
    __tablename__ = "overall_stats"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_epidemic = Column(Integer, ForeignKey('epidemic.id', ondelete='CASCADE', name='fk_overall_stats_epidemic'), nullable=False)
    total_cases = Column(Integer, default=0)
    total_deaths = Column(Integer, default=0)
    fatality_ratio = Column(Float, default=0.0)
    
    epidemic = relationship("Epidemic", back_populates="overall_stats")
    
    __table_args__ = (Index('idx_overall_epidemic', id_epidemic),) 
    