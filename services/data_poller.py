import asyncio
import httpx
import os
import logging

logger = logging.getLogger("uvicorn.info")

from database import SessionLocal
from models import AlertRuleModel, Condition
from services.alert_delivery import AlertDeliveryService

# Default URLs (can be overridden by env vars)
KOSTAL_REALTIME_URL = os.getenv("KOSTAL_SERVICE_URL", "http://kostal-ms:8082/kostal/realtimedata")  # NOSONAR
FRONIUS_REALTIME_URL = os.getenv("FRONIUS_SERVICE_URL", "http://fronius-ms:8081/fronius/realtimedata")  # NOSONAR

async def fetch_data(client, url, service_name):
    try:
        logger.info(f"Polling {service_name} at {url}...")
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        logger.info(f"Successfully fetched {service_name} data: {str(data)[:200]}...")
        return data
    except httpx.RequestError as e:
        logger.error(f"Network error polling {service_name}: {e}")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error polling {service_name}: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        logger.error(f"Unexpected error polling {service_name}: {e}")
    return None

def evaluate_condition(actual_value, threshold, condition):
    """
    Evaluates whether the actual value violates the threshold based on the condition.
    """
    if condition == Condition.GREATER_THAN:
        return actual_value > threshold
    elif condition == Condition.LESS_THAN:
        return actual_value < threshold
    elif condition == Condition.EQUALS:
        return actual_value == threshold
    return False

async def process_inverter_data(data, delivery_service):
    """
    Processes the inverter data, checks against alert rules, and triggers alerts if necessary.
    """
    realtime_data = data.get("realtime_data", {})
    if not realtime_data:
        return

    db = SessionLocal()
    try:
        for metric_type, metric_info in realtime_data.items():
            value = metric_info.get("value")
            if value is None:
                continue
            
            # Ensure value is a float for comparison
            try:
                actual_value = float(value)
            except (ValueError, TypeError):
                continue

            # Fetch all active rules for this metric type
            rules = db.query(AlertRuleModel).filter(
                AlertRuleModel.metric_type == metric_type,
                AlertRuleModel.is_active == True
            ).all()

            for rule in rules:
                if evaluate_condition(actual_value, rule.threshold_value, rule.condition):
                    await delivery_service.send_alert(rule, actual_value)
    finally:
        db.close()

async def poll_data_services():
    """
    Constantly queries the Kostal and Fronius services for real-time data.
    """
    delivery_service = AlertDeliveryService()
    async with httpx.AsyncClient() as client:
        while True:
            # Fetch data from both services concurrently
            results = await asyncio.gather(
                fetch_data(client, KOSTAL_REALTIME_URL, "Kostal"),
                fetch_data(client, FRONIUS_REALTIME_URL, "Fronius")
            )
            
            for data in results:
                if data:
                    await process_inverter_data(data, delivery_service)
            
            # Wait for 60 seconds before next poll
            await asyncio.sleep(60)
