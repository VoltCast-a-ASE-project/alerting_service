from unittest.mock import patch, AsyncMock
from models import Condition

def test_ingest_data_triggers_alert(client):
    # Create a rule
    client.post(
        "/alert/api/v1/rules",
        json={
            "user_id": "user1",
            "metric_type": "temperature",
            "threshold_value": 30.0,
            "condition": "GREATER_THAN",
            "delivery_channel": "EMAIL"
        }
    )
    
    # We need to patch the method on the instance that is already created in routers.ingestion
    with patch("routers.ingestion.alert_delivery_service.send_alert", new_callable=AsyncMock) as mock_send_alert:
        response = client.post(
            "/alert/api/v1/data/ingest",
            json={
                "user_id": "user1",
                "metric_type": "temperature",
                "value": 35.0,
                "timestamp": "2023-10-27T10:00:00"
            }
        )
        assert response.status_code == 200
        
        # Verify the mock was called
        mock_send_alert.assert_called_once()
        
        # Verify arguments
        args, _ = mock_send_alert.call_args
        rule = args[0]
        value = args[1]
        assert rule.user_id == "user1"
        assert value == 35.0

def test_ingest_data_no_alert(client):
    # Create a rule
    client.post(
        "/alert/api/v1/rules",
        json={
            "user_id": "user1",
            "metric_type": "temperature",
            "threshold_value": 30.0,
            "condition": "GREATER_THAN",
            "delivery_channel": "EMAIL"
        }
    )
    
    with patch("routers.ingestion.alert_delivery_service.send_alert", new_callable=AsyncMock) as mock_send_alert:
        response = client.post(
            "/alert/api/v1/data/ingest",
            json={
                "user_id": "user1",
                "metric_type": "temperature",
                "value": 25.0,
                "timestamp": "2023-10-27T10:00:00"
            }
        )
        assert response.status_code == 200
        mock_send_alert.assert_not_called()
