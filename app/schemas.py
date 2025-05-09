from pydantic import BaseModel
from typing import Optional
from datetime import datetime 

class SensorDataBase(BaseModel):
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    luminosity: Optional[float] = None
    lights_status: Optional[bool] = None
    water_pump_status: Optional[bool] = None

class SensorDataCreate(SensorDataBase):
    pass

class SensorData(SensorDataBase):
    id: int

    class Config:
        from_attributes = True 

class RuleBase(BaseModel):
    name: str
    device_type: str
    temperature_condition: Optional[str] = None
    temperature_value: Optional[float] = None
    humidity_condition: Optional[str] = None
    humidity_value: Optional[float] = None
    luminosity_condition: Optional[str] = None
    luminosity_value: Optional[float] = None
    duration_minutes: int = 10
    check_interval_minutes: int = 30
    is_active: bool = True

class RuleCreate(RuleBase):
    pass

class RuleUpdate(BaseModel):
    name: Optional[str] = None
    temperature_condition: Optional[str] = None
    temperature_value: Optional[float] = None
    humidity_condition: Optional[str] = None
    humidity_value: Optional[float] = None
    luminosity_condition: Optional[str] = None
    luminosity_value: Optional[float] = None
    duration_minutes: Optional[int] = None
    check_interval_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class Rule(RuleBase):
    id: int
    created_at: datetime
    last_triggered: Optional[datetime] = None

    class Config:
        from_attributes = True