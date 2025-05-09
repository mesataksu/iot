from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional
import time
import asyncio

from ..database import get_db, SessionLocal
from ..models import SensorData
from .. import schemas, crud

router = APIRouter()

@router.get("/temperature", response_model=float)
def get_temperature(db: Session = Depends(get_db)):
    """Get current temperature"""
    sensor_data = crud.get_or_create_sensor_data(db)
    return sensor_data.temperature

@router.post("/temperature", response_model=float)
def set_temperature(temperature: float, db: Session = Depends(get_db)):
    """Set temperature value"""
    sensor_data = crud.update_sensor_data(db, schemas.SensorDataCreate(temperature=temperature))
    return sensor_data.temperature

@router.get("/humidity", response_model=float)
def get_humidity(db: Session = Depends(get_db)):
    """Get current humidity"""
    sensor_data = crud.get_or_create_sensor_data(db)
    return sensor_data.humidity

@router.post("/humidity", response_model=float)
def set_humidity(humidity: float, db: Session = Depends(get_db)):
    """Set humidity value"""
    sensor_data = crud.update_sensor_data(db, schemas.SensorDataCreate(humidity=humidity))
    return sensor_data.humidity

@router.get("/luminosity", response_model=float)
def get_luminosity(db: Session = Depends(get_db)):
    """Get current luminosity"""
    sensor_data = crud.get_or_create_sensor_data(db)
    return sensor_data.luminosity

@router.post("/luminosity", response_model=float)
def set_luminosity(luminosity: float, db: Session = Depends(get_db)):
    """Set luminosity value"""
    sensor_data = crud.update_sensor_data(db, schemas.SensorDataCreate(luminosity=luminosity))
    return sensor_data.luminosity

@router.get("/lights", response_model=bool)
def get_lights_status(db: Session = Depends(get_db)):
    """Get lights status"""
    sensor_data = crud.get_or_create_sensor_data(db)
    return sensor_data.lights_status

@router.post("/lights", response_model=bool)
def set_lights_status(status: bool, db: Session = Depends(get_db)):
    """Set lights status"""
    sensor_data = crud.update_sensor_data(db, schemas.SensorDataCreate(lights_status=status))
    return sensor_data.lights_status

@router.get("/water-pump", response_model=bool)
def get_water_pump_status(db: Session = Depends(get_db)):
    """Get water pump status"""
    sensor_data = crud.get_or_create_sensor_data(db)
    return sensor_data.water_pump_status

@router.post("/water-pump", response_model=bool)
def set_water_pump_status(status: bool, db: Session = Depends(get_db)):
    """Set water pump status"""
    sensor_data = crud.update_sensor_data(db, schemas.SensorDataCreate(water_pump_status=status))
    return sensor_data.water_pump_status

@router.post("/lights/timed")
def control_lights_with_timer(
    duration_minutes: int = Query(..., description="Duration in minutes to keep the lights on"),
    db: Session = Depends(get_db)
):
    """
    Turn on lights with timer
    
    Lights will automatically turn off after the specified duration
    """
    def get_db_session():
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()
   
    crud.control_lights_with_timer(db, duration_minutes, get_db_session)
   
    return {
        "message": f"Lights turned on and will automatically turn off after {duration_minutes} minutes"
    }

@router.post("/water_pump/timed")
def control_water_pump_with_timer(
    duration_minutes: int = Query(..., description="Duration in minutes to keep the water pump on"),
    db: Session = Depends(get_db)
):
    """
    Turn on water pump with timer
    
    Water pump will automatically turn off after the specified duration
    """
    def get_db_session():
        db = SessionLocal()
        try:
            return db
        finally:
            db.close()

    crud.control_water_pump_with_timer(db, duration_minutes, get_db_session)
   
    return {
        "message": f"Water pump turned on and will automatically turn off after {duration_minutes} minutes"
    }

@router.get("/timers/status")
def get_timer_status():
    """
    Control timers
    """
    return crud.get_timer_status()