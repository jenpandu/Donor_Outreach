def test_create_outbound_message(client):
    campaign_response = client.post("/campaigns", json={
        "name": "Msg Test Campaign",
        "goal_amt": 3000,
        "description": "Campaign for message tests",
        "def_lang": "en"
    })
    print(campaign_response.status_code, campaign_response.get_json())
    campaign_id = campaign_response.get_json()["id"]

    response = client.post(f"/campaigns/{campaign_id}/messages/outbound", json={
        "donor_name": "Jane Doe",
        "original_text": "Thank you for your support.",
        "target_language": "en"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["direction"] == "outbound"
    assert data["original_language"] == "en"
    assert data["translated_text"] == "Thank you for your support."  # same-language short-circuit


def test_create_inbound_message(client):
    campaign_response = client.post("/campaigns", json={
        "name": "Msg Test Campaign",
        "goal_amt": 3000,
        "description": "Campaign for message tests",
        "def_lang": "en"
    })
    campaign_id = campaign_response.get_json()["id"]

    response = client.post(f"/campaigns/{campaign_id}/messages/inbound", json={
        "donor_name": "Jane Doe",
        "original_text": "Thank you!"
    })

    assert response.status_code == 201
    data = response.get_json()
    assert data["direction"] == "inbound"
    assert data["target_language"] == "en"


def test_get_message_by_id(client):
    campaign_response = client.post("/campaigns", json={
        "name": "Msg Test Campaign",
        "goal_amt": 3000,
        "description": "Campaign for message tests",
        "def_lang": "en"
    })
    campaign_id = campaign_response.get_json()["id"]

    create_response = client.post(f"/campaigns/{campaign_id}/messages/outbound", json={
        "donor_name": "Jane Doe",
        "original_text": "Thank you for your support.",
        "target_language": "en"
    })
    message_id = create_response.get_json()["id"]

    response = client.get(f"/messages/{message_id}")

    assert response.status_code == 200
    assert response.get_json()["id"] == message_id


def test_update_message(client):
    campaign_response = client.post("/campaigns", json={
        "name": "Msg Test Campaign",
        "goal_amt": 3000,
        "description": "Campaign for message tests",
        "def_lang": "en"
    })
    campaign_id = campaign_response.get_json()["id"]

    create_response = client.post(f"/campaigns/{campaign_id}/messages/outbound", json={
        "donor_name": "Jane Doe",
        "original_text": "Original text.",
        "target_language": "en"
    })
    message_id = create_response.get_json()["id"]

    update_response = client.put(f"/messages/{message_id}", json={
        "original_text": "Corrected text."
    })

    assert update_response.status_code == 200
    assert update_response.get_json()["original_text"] == "Corrected text."


def test_delete_message(client):
    campaign_response = client.post("/campaigns", json={
        "name": "Msg Test Campaign",
        "goal_amt": 3000,
        "description": "Campaign for message tests",
        "def_lang": "en"
    })
    campaign_id = campaign_response.get_json()["id"]

    create_response = client.post(f"/campaigns/{campaign_id}/messages/outbound", json={
        "donor_name": "Jane Doe",
        "original_text": "To be deleted.",
        "target_language": "en"
    })
    message_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/messages/{message_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/messages/{message_id}")
    assert get_response.status_code == 404