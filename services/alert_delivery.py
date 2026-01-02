import os
import resend
import logging
from models import AlertRuleModel, DeliveryChannel

logger = logging.getLogger("uvicorn.info")

class AlertDeliveryService:
    def __init__(self):
        self.api_key = os.environ.get("RESEND_API_KEY")
        if self.api_key:
             resend.api_key = self.api_key
        else:
             logger.warning("Warning: RESEND_API_KEY not found in environment.")

    async def send_alert(self, rule: AlertRuleModel, actual_value: float):
        logger.info(f"[ALERT TRIGGERED for User {rule.user_id}]: {rule.metric_type} ({actual_value}) violated rule (Condition: {rule.condition} {rule.threshold_value}) via Channel: {rule.delivery_channel}")

        if rule.delivery_channel == DeliveryChannel.EMAIL:
            if not self.api_key:
                logger.warning("Skipping email alert: No API Key configured.")
                return

            try:
                # Use user_id as email if it looks like one, otherwise use a testing email
                to_email = rule.user_id if "@" in rule.user_id else "delivered@resend.dev"
                
                params = {
                    "from": "onboarding@resend.dev",
                    "to": [to_email],
                    "subject": f"Alert Triggered: {rule.metric_type}",
                    "html": f"""
                        <h1>Alert Triggered</h1>
                        <p><strong>Metric:</strong> {rule.metric_type}</p>
                        <p><strong>Current Value:</strong> {actual_value}</p>
                        <p><strong>Threshold:</strong> {rule.threshold_value}</p>
                        <p><strong>Condition:</strong> {rule.condition}</p>
                    """,
                }

                email = resend.Emails.send(params)
                logger.info(f"Email sent successfully: {email}")
            except Exception as e:
                logger.error(f"Failed to send email: {e}")
