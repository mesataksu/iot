from fastapi import APIRouter, Depends, HTTPException, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional

from ..database import get_db
from .. import models, schemas, crud

router = APIRouter()

@router.post("/rules", response_model=schemas.Rule)
def create_rule(rule: schemas.RuleCreate, db: Session = Depends(get_db)):
    """Create a new automation rule"""
    return crud.create_rule(db, rule)

@router.get("/rules", response_model=List[schemas.Rule])
def read_rules(
    skip: int = 0, 
    limit: int = 100, 
    device_type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db)
):
    """Get all rules with optional filtering"""
    query = db.query(models.Rule)
    
    if device_type:
        query = query.filter(models.Rule.device_type == device_type)
    
    if is_active is not None:
        query = query.filter(models.Rule.is_active == is_active)
        
    return query.offset(skip).limit(limit).all()

@router.get("/rules/{rule_id}", response_model=schemas.Rule)
def read_rule(rule_id: int = Path(...), db: Session = Depends(get_db)):
    """Get a specific rule by ID"""
    rule = crud.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/rules/{rule_id}", response_model=schemas.Rule)
def update_rule(
    rule_update: schemas.RuleUpdate, 
    rule_id: int = Path(...), 
    db: Session = Depends(get_db)
):
    """Update a rule"""
    rule = crud.update_rule(db, rule_id, rule_update)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.delete("/rules/{rule_id}")
def delete_rule(rule_id: int = Path(...), db: Session = Depends(get_db)):
    """Delete a rule"""
    success = crud.delete_rule(db, rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="Rule not found")
    return {"message": "Rule deleted successfully"}

@router.post("/rules/{rule_id}/toggle", response_model=schemas.Rule)
def toggle_rule_status(rule_id: int = Path(...), db: Session = Depends(get_db)):
    """Toggle rule active status"""
    rule = crud.get_rule(db, rule_id)
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    
    rule_update = schemas.RuleUpdate(is_active=not rule.is_active)
    return crud.update_rule(db, rule_id, rule_update)