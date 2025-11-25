from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from models import AlertRuleSchema, AlertRuleModel
from database import get_db

router = APIRouter()

@router.post("/api/v1/rules", response_model=AlertRuleSchema)
def create_rule(rule: AlertRuleSchema, db: Session = Depends(get_db)):
    db_rule = AlertRuleModel(**rule.dict())
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule

@router.get("/api/v1/rules/{user_id}", response_model=List[AlertRuleSchema])
def get_rules_for_user(user_id: str, db: Session = Depends(get_db)):
    rules = db.query(AlertRuleModel).filter(AlertRuleModel.user_id == user_id, AlertRuleModel.is_active == True).all()
    return rules

@router.delete("/api/v1/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    db_rule = db.query(AlertRuleModel).filter(AlertRuleModel.id == rule_id).first()
    if db_rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    db_rule.is_active = False
    db.commit()
    return {"message": "Rule deactivated"}
