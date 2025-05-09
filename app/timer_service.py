from datetime import datetime, timedelta
import threading
import time
from sqlalchemy.sql import func
from typing import Dict, Callable, Any, Optional

class DeviceTimer:
    def __init__(self, device_name: str, duration_minutes: int, callback: Callable):
        self.device_name = device_name
        self.end_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.callback = callback
        self.cancelled = False

    def is_expired(self) -> bool:
        return datetime.now() >= self.end_time or self.cancelled

    def get_remaining_minutes(self) -> int:
        if self.cancelled:
            return 0
        time_diff = self.end_time - datetime.now()
        return max(0, int(time_diff.total_seconds()))

    def cancel(self):
        self.cancelled = True


class TimerService:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(TimerService, cls).__new__(cls)
                cls._instance.timers = {}
                cls._instance.is_running = False
                cls._instance.thread = None
            return cls._instance

    def start_timer(self, device_name: str, duration_minutes: int, callback: Callable[[], Any]) -> str:
        """Start a timer for the specified device"""
        timer_id = f"{device_name}_{datetime.now().timestamp()}"
        self.timers[timer_id] = DeviceTimer(device_name, duration_minutes, callback)
        
       
        if not self.is_running:
            self._start_timer_thread()
        
        return timer_id

    def cancel_timer(self, device_name: str) -> bool:
        """Cancel all timers for the specified device"""
        cancelled = False
        for timer_id, timer in list(self.timers.items()):
            if timer.device_name == device_name:
                timer.cancel()
                cancelled = True
        return cancelled

    def get_device_timer(self, device_name: str) -> Optional[DeviceTimer]:
        """Get the active timer for a device if it exists"""
        for timer in self.timers.values():
            if timer.device_name == device_name and not timer.is_expired():
                return timer
        return None

    def _check_timers(self):
        """Check all timers and execute callbacks for expired ones"""
        for timer_id, timer in list(self.timers.items()):
            if timer.is_expired():
                try:
                    timer.callback()
                except Exception as e:
                    print(f"Error executing timer callback: {e}")
                self.timers.pop(timer_id, None)

    def _timer_loop(self):
        """Main timer checking loop"""
        while self.is_running:
            self._check_timers()
            time.sleep(1)

    def _start_timer_thread(self):
        """Start the timer checking thread"""
        self.is_running = True
        self.thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.thread.start()
        print("Timer service started")

    def stop(self):
        """Stop the timer service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
            print("Timer service stopped")


def create_lights_off_callback(db_factory):
    def turn_lights_off():
        try:
            db = db_factory()
            try:
                from . import crud
                sensor_data = crud.get_or_create_sensor_data(db)
                if sensor_data.lights_status:
                    print(f"[{datetime.now()}] Auto-turning off lights based on timer")
                    sensor_data.lights_status = False
                    sensor_data.lights_status_timestamp = func.now()
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"Error in lights_off_callback: {e}")
    return turn_lights_off

def create_water_pump_off_callback(db_factory):
    def turn_water_pump_off():
        try:
            db = db_factory()
            try:
                from . import crud
                sensor_data = crud.get_or_create_sensor_data(db)
                if sensor_data.water_pump_status:
                    print(f"[{datetime.now()}] Auto-turning off water pump based on timer")
                    sensor_data.water_pump_status = False
                    sensor_data.water_pump_status_timestamp = func.now()
                    db.commit()
            finally:
                db.close()
        except Exception as e:
            print(f"Error in water_pump_off_callback: {e}")
    return turn_water_pump_off