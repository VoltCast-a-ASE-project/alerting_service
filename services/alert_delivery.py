from models import AlertRuleModel

class AlertDeliveryService:
    async def send_alert(self, rule: AlertRuleModel, actual_value: float):
        print(f"[ALERT TRIGGERED for User {rule.user_id}]: {rule.metric_type} ({actual_value}) violated rule (Condition: {rule.condition} {rule.threshold_value}) via Channel: {rule.delivery_channel}")
