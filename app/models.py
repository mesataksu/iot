from sqlalchemy import Column, Integer, Float, String, Boolean, DateTime
from sqlalchemy.sql import func
from .database import Base

class SensorData(Base):
    """
    Model to store sensor data and device statuses
    """
    __tablename__ = "sensor_data"
    id = Column(Integer, primary_key=True, index=True)
    
    temperature = Column(Float, nullable=False, default=0.0)
    temperature_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    humidity = Column(Float, nullable=False, default=0.0)
    humidity_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    luminosity = Column(Float, nullable=False, default=0.0)
    luminosity_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    lights_status = Column(Boolean, default=False)
    lights_status_timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    water_pump_status = Column(Boolean, default=False)
    water_pump_status_timestamp = Column(DateTime(timezone=True), server_default=func.now())

class Rule(Base):
    """
    Model to store automation rules for devices
    """
    __tablename__ = "rules"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    
    temperature_condition = Column(String, nullable=True)  # ">" or "<" or None
    temperature_value = Column(Float, nullable=True)
    
    humidity_condition = Column(String, nullable=True)
    humidity_value = Column(Float, nullable=True)
    
    luminosity_condition = Column(String, nullable=True)
    luminosity_value = Column(Float, nullable=True)
    
    # Actions
    duration_minutes = Column(Integer, nullable=False, default=10)
    check_interval_minutes = Column(Integer, nullable=False, default=30)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_triggered = Column(DateTime(timezone=True), nullable=True)