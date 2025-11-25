from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from models import IngestionData, AlertRuleModel, Condition
from database import get_db
from services.alert_delivery import AlertDeliveryService

router = APIRouter()
alert_delivery_service = AlertDeliveryService()


@router.post("/api/v1/data/ingest")
async def ingest_data(
    data: IngestionData,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    rules = (
        db.query(AlertRuleModel)
        .filter(
            AlertRuleModel.user_id == data.user_id,
            AlertRuleModel.metric_type == data.metric_type,
            AlertRuleModel.is_active,
        )
        .all()
    )

    for rule in rules:
        violated = False
        if (
            rule.condition == Condition.GREATER_THAN
            and data.value > rule.threshold_value
        ):
            violated = True
        elif (
            rule.condition == Condition.LESS_THAN and data.value < rule.threshold_value
        ):
            violated = True
        elif rule.condition == Condition.EQUALS and data.value == rule.threshold_value:
            violated = True

        if violated:
            background_tasks.add_task(
                alert_delivery_service.send_alert, rule, data.value
            )

    return {"message": "Data processed"}
