from models import Condition, DeliveryChannel

def test_create_rule(client):
    response = client.post(
        "/alert/api/v1/rules",
        json={
            "user_id": "user1",
            "metric_type": "temperature",
            "threshold_value": 30.0,
            "condition": "GREATER_THAN",
            "delivery_channel": "EMAIL"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user_id"] == "user1"
    assert data["metric_type"] == "temperature"
    assert data["condition"] == "GREATER_THAN"
    assert "id" in data

def test_get_rules_for_user(client):
    # Create a rule first
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
    
    response = client.get("/alert/api/v1/rules/user1")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["user_id"] == "user1"

def test_delete_rule(client):
    # Create a rule first
    create_response = client.post(
        "/alert/api/v1/rules",
        json={
            "user_id": "user1",
            "metric_type": "temperature",
            "threshold_value": 30.0,
            "condition": "GREATER_THAN",
            "delivery_channel": "EMAIL"
        }
    )
    rule_id = create_response.json()["id"]
    
    # Delete the rule
    delete_response = client.delete(f"/alert/api/v1/rules/{rule_id}")
    assert delete_response.status_code == 200
    assert delete_response.json() == {"message": "Rule deactivated"}
    
    # Verify it's not returned in get_rules
    get_response = client.get("/alert/api/v1/rules/user1")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0
