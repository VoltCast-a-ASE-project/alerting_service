import pytest
from services.alert_delivery import AlertDeliveryService
from models import AlertRuleModel, Condition

@pytest.mark.asyncio
async def test_send_alert(capsys):
    service = AlertDeliveryService()
    rule = AlertRuleModel(
        user_id="user1",
        metric_type="temperature",
        condition="GREATER_THAN",
        threshold_value=30.0,
        delivery_channel="email"
    )
    actual_value = 35.0
    
    await service.send_alert(rule, actual_value)
    
    captured = capsys.readouterr()
    # The print statement in the service:
    # print(f"[ALERT TRIGGERED for User {rule.user_id}]: {rule.metric_type} ({actual_value}) violated rule (Condition: {rule.condition} {rule.threshold_value}) via Channel: {rule.delivery_channel}")
    
    expected_output = "[ALERT TRIGGERED for User user1]: temperature (35.0) violated rule (Condition: GREATER_THAN 30.0) via Channel: email\n"
    
    # Normalize line endings just in case
    assert captured.out.strip() == expected_output.strip()
