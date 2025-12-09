from sqlalchemy import Column, Integer, String, Float, Boolean
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from enum import Enum

from database import Base

class Condition(str, Enum):
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    EQUALS = "EQUALS"

class DeliveryChannel(str, Enum):
    EMAIL = "EMAIL"
    DASHBOARD = "DASHBOARD"
    SMS = "SMS"

class AlertRuleModel(Base):
    __tablename__ = "alert_rules"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    metric_type = Column(String)
    threshold_value = Column(Float)
    condition = Column(String)
    is_active = Column(Boolean, default=True)
    delivery_channel = Column(String)

class AlertRuleBase(BaseModel):
    user_id: str
    metric_type: str
    threshold_value: float
    condition: Condition
    delivery_channel: DeliveryChannel

class AlertRuleCreate(AlertRuleBase):
    pass

class AlertRule(AlertRuleBase):
    id: int
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class IngestionData(BaseModel):
    user_id: str
    metric_type: str
    value: float
    timestamp: datetime
