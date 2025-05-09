# rule_service.py
import threading
import time
from datetime import datetime, timedelta
from typing import List, Callable, Dict
from sqlalchemy.orm import Session

class RuleChecker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(RuleChecker, cls).__new__(cls)
                cls._instance.is_running = False
                cls._instance.thread = None
                cls._instance.db_factory = None
                cls._instance.rules_last_checked = {}
            return cls._instance

    def start(self, db_factory):
        """Start the rule checking service"""
        self.db_factory = db_factory
        
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._rule_check_loop, daemon=True)
            self.thread.start()
            print("Rule checking service started")

    def stop(self):
        """Stop the rule checking service"""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=1)
            print("Rule checking service stopped")

    def _rule_check_loop(self):
        """Main rule checking loop"""
        while self.is_running:
            try:
                self._check_rules()
            except Exception as e:
                print(f"Error checking rules: {e}")
            time.sleep(60)  # Check every minute

    def _check_rules(self):
        """Check all active rules and trigger actions if conditions are met"""
        db = self.db_factory()
        try:
            from . import crud, models
            
            rules = db.query(models.Rule).filter(models.Rule.is_active == True).all()
            
            sensor_data = crud.get_or_create_sensor_data(db)
            
            current_time = datetime.now()
            
            for rule in rules:
                rule_key = f"{rule.device_type}_{rule.id}"
                last_checked = self.rules_last_checked.get(rule_key)
                
                if last_checked is None or (current_time - last_checked).total_seconds() >= rule.check_interval_minutes * 60:
                    self.rules_last_checked[rule_key] = current_time
                    
                    conditions_met = self._evaluate_conditions(rule, sensor_data)
                    
                    if conditions_met:
                        print(f"[{current_time}] Rule '{rule.name}' conditions met, triggering action for {rule.device_type}")
                        
                        if rule.device_type == "water_pump":
                            crud.control_water_pump_with_timer(db, rule.duration_minutes, self.db_factory)
                        elif rule.device_type == "lights":
                            crud.control_lights_with_timer(db, rule.duration_minutes, self.db_factory)
                        
                        rule.last_triggered = current_time
                        db.commit()
                
        finally:
            db.close()

    def _evaluate_conditions(self, rule, sensor_data):
        """Evaluate all conditions of a rule against current sensor data"""
        conditions_met = True
        
        if rule.temperature_condition and rule.temperature_value is not None:
            if rule.temperature_condition == ">" and not (sensor_data.temperature > rule.temperature_value):
                conditions_met = False
            elif rule.temperature_condition == "<" and not (sensor_data.temperature < rule.temperature_value):
                conditions_met = False
                
        if rule.humidity_condition and rule.humidity_value is not None:
            if rule.humidity_condition == ">" and not (sensor_data.humidity > rule.humidity_value):
                conditions_met = False
            elif rule.humidity_condition == "<" and not (sensor_data.humidity < rule.humidity_value):
                conditions_met = False
        
        if rule.luminosity_condition and rule.luminosity_value is not None:
            if rule.luminosity_condition == ">" and not (sensor_data.luminosity > rule.luminosity_value):
                conditions_met = False
            elif rule.luminosity_condition == "<" and not (sensor_data.luminosity < rule.luminosity_value):
                conditions_met = False
                
        return conditions_met