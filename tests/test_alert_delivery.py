import pytest
import os
from unittest.mock import patch, MagicMock
from services.alert_delivery import AlertDeliveryService
from models import AlertRuleModel, Condition, DeliveryChannel

@pytest.fixture
def mock_resend():
    with patch("services.alert_delivery.resend") as mock:
        yield mock

@pytest.fixture
def alert_rule():
    return AlertRuleModel(
        user_id="test@example.com",
        metric_type="temperature",
        condition=Condition.GREATER_THAN,
        threshold_value=30.0,
        delivery_channel=DeliveryChannel.EMAIL
    )

def test_init_reads_from_env():
    with patch.dict(os.environ, {"RESEND_API_KEY": "secret_key_from_env"}):
        service = AlertDeliveryService()
        assert service.api_key == "secret_key_from_env"

def test_init_no_key_logs_warning():
    with patch.dict(os.environ, {}, clear=True):
        service = AlertDeliveryService()
        assert service.api_key is None        


@pytest.mark.asyncio
async def test_send_alert_email_success(mock_resend, alert_rule):
    with patch.dict(os.environ, {"RESEND_API_KEY": "test_key"}):
        service = AlertDeliveryService()
    
    mock_resend.Emails.send.return_value = {"id": "email_123"}
    
    await service.send_alert(alert_rule, 35.0)
    
    mock_resend.Emails.send.assert_called_once()
    call_args = mock_resend.Emails.send.call_args[0][0]
    assert call_args["to"] == ["test@example.com"]
    assert "Alert Triggered" in call_args["subject"]
    assert "35.0" in call_args["html"]
    
@pytest.mark.asyncio
async def test_send_alert_skips_if_no_api_key(mock_resend, alert_rule):
    with patch.dict(os.environ, {}, clear=True):
        service = AlertDeliveryService()
        
    await service.send_alert(alert_rule, 35.0)
    
    mock_resend.Emails.send.assert_not_called()

@pytest.mark.asyncio
async def test_send_alert_handles_exception(mock_resend, alert_rule):
    with patch.dict(os.environ, {"RESEND_API_KEY": "test_key"}):
        service = AlertDeliveryService()
        
    mock_resend.Emails.send.side_effect = Exception("API Error")
    
    await service.send_alert(alert_rule, 35.0)
    
@pytest.mark.asyncio
async def test_send_alert_non_email_channel(mock_resend):
    rule = AlertRuleModel(
        user_id="user1",
        metric_type="cpu",
        condition=Condition.EQUALS,
        threshold_value=90.0,
        delivery_channel=DeliveryChannel.SMS
    )
    
    with patch.dict(os.environ, {"RESEND_API_KEY": "test_key"}):
        service = AlertDeliveryService()
        
    await service.send_alert(rule, 95.0)
    
    mock_resend.Emails.send.assert_not_called()
