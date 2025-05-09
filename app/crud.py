from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from . import models, schemas
from .timer_service import TimerService, create_lights_off_callback, create_water_pump_off_callback


def get_or_create_sensor_data(db: Session):
    """
    Get existing sensor data or create a new record if none exists
    """
    sensor_data = db.query(models.SensorData).first()
    if not sensor_data:
        sensor_data = models.SensorData()
        db.add(sensor_data)
        db.commit()
        db.refresh(sensor_data)
    return sensor_data

def update_sensor_data(db: Session, sensor_data_update: schemas.SensorDataCreate):
    """
    Update sensor data with appropriate timestamps
    """
    sensor_data = get_or_create_sensor_data(db)

    update_data = sensor_data_update.dict(exclude_unset=True)
    
    for key, value in update_data.items():
        setattr(sensor_data, key, value)
        
        if key == 'temperature':
            sensor_data.temperature_timestamp = func.now()
        elif key == 'humidity':
            sensor_data.humidity_timestamp = func.now()
        elif key == 'luminosity':
            sensor_data.luminosity_timestamp = func.now()
        elif key == 'lights_status':
            sensor_data.lights_status_timestamp = func.now()
        elif key == 'water_pump_status':
            sensor_data.water_pump_status_timestamp = func.now()
   
    db.commit()
    db.refresh(sensor_data)
    return sensor_data


def control_lights_with_timer(db: Session, duration_minutes: int = None, db_factory = None):
    """
    Control lights with timer
    """
    from . import crud 
    sensor_data = crud.get_or_create_sensor_data(db)
    sensor_data.lights_status = True
    db.commit()
    db.refresh(sensor_data)
    
    timer_service = TimerService()
    
    if duration_minutes and duration_minutes > 0:
        lights_off_callback = create_lights_off_callback(db_factory)
        timer_service.start_timer("lights", duration_minutes, lights_off_callback)
    
    return sensor_data

def control_water_pump_with_timer(db: Session, duration_minutes: int = None, db_factory = None):
    """
    Control water pump with timer
    """

    from . import crud
    sensor_data = crud.get_or_create_sensor_data(db)
    sensor_data.water_pump_status = True
    db.commit()
    db.refresh(sensor_data)
    
    timer_service = TimerService()
    
    if duration_minutes and duration_minutes > 0:
        water_pump_off_callback = create_water_pump_off_callback(db_factory)
        timer_service.start_timer("water_pump", duration_minutes, water_pump_off_callback)
    
    return sensor_data

def get_timer_status():
    """
    Get the status of active timers
    """
    timer_service = TimerService()
    
    lights_timer = timer_service.get_device_timer("lights")
    water_pump_timer = timer_service.get_device_timer("water_pump")
    
    return {
        "lights": {
            "active": lights_timer is not None,
            "remaining_seconds": lights_timer.get_remaining_minutes() if lights_timer else 0
        },
        "water_pump": {
            "active": water_pump_timer is not None,
            "remaining_seconds": water_pump_timer.get_remaining_minutes() if water_pump_timer else 0
        }
    }

def create_rule(db: Session, rule: schemas.RuleCreate):
    """Create a new rule"""
    db_rule = models.Rule(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

def get_rules(db: Session, skip: int = 0, limit: int = 100):
    """Get all rules"""
    return db.query(models.Rule).offset(skip).limit(limit).all()

def get_rule(db: Session, rule_id: int):
    """Get a specific rule by ID"""
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first()

def get_active_rules_by_device(db: Session, device_type: str):
    """Get all active rules for a specific device type"""
    return db.query(models.Rule).filter(
        models.Rule.device_type == device_type,
        models.Rule.is_active == True
    ).all()

def update_rule(db: Session, rule_id: int, rule_update: schemas.RuleUpdate):
    """Update an existing rule"""
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if db_rule:
        update_data = rule_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_rule, key, value)
        db.commit()
        db.refresh(db_rule)
    return db_rule

def delete_rule(db: Session, rule_id: int):
    """Delete a rule"""
    db_rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
    if db_rule:
        db.delete(db_rule)
        db.commit()
        return True
    return False