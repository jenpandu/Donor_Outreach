# inputting invalid data
def test_create_invalid_campaign(client):
    response = client.post("/campaigns", json={
        "name": "Test Campaign",
        "goal_amt": -100,
        "description": "Incorrect Test",
        "def_lang": "en"
    })
    assert response.status_code == 422

def test_create_campaign_returns_201(client):
    response = client.post("/campaigns", json={
        "name": "Test Campaign",
        "goal_amt": 5000,
        "description": "A test campaign",
        "def_lang": "en"
    })
    assert response.status_code == 201
    data = response.get_json()
    assert data["name"] == "Test Campaign"
    assert data["def_lang"] == "en"

def test_get_campaign_by_id(client):
    create_response = client.post("/campaigns", json ={
        "name": "Test Campaign",
        "goal_amt": 5000,
        "description": "A test campaign",
        "def_lang": "en"
    })
    campaign_id = create_response.get_json()["id"]

    response = client.get(f"/campaigns/{campaign_id}")

    assert response.status_code == 200
    data = response.get_json()
    assert data["id"] == campaign_id
    assert data["name"] == "Test Campaign"

def test_get_nonexistent_campaign_returns_404(client):
    response = client.get(f"/campaigns/999999")
    assert response.status_code == 404


def test_list_campaigns(client):
    client.post("/campaigns", json={
        "name": "Test Campaign",
        "goal_amt": 5000,
        "description": "A test campaign",
        "def_lang": "en"
    })

    client.post("/campaigns", json ={
        "name": "Testing",
        "goal_amt": 1000,
        "description": "A campaign to test",
        "def_lang": "es"
    })
    client.post("/campaigns", json ={
        "name": "Mary",
        "goal_amt": 100,
        "description": "Raise money for school dance",
        "def_lang": "en"
    })

    response = client.get(f"/campaigns")

    assert response.status_code == 200
    data = response.get_json()
    assert data["count"] == 3
    assert len(data["items"]) == 3

def test_partial_update_on_campaign(client):
    create_response = client.post("/campaigns", json={
        "name": "Original Name",
        "goal_amt": 5000,
        "description": "Original description",
        "def_lang": "en"
    })
    campaign_id = create_response.get_json()["id"]

    update_response = client.put(f"/campaigns/{campaign_id}", json={
        "description": "Updated description"
    })

    assert update_response.status_code == 200
    data = update_response.get_json()
    assert data["description"] == "Updated description"

def test_full_update_on_campaign(client):
    create_response = client.post("/campaigns", json={
        "name": "Original Name",
        "goal_amt": 5000,
        "description": "Original description",
        "def_lang": "en"
    })
    campaign_id = create_response.get_json()["id"]

    updated_response = client.put(f"/campaigns/{campaign_id}", json={
        "name": "updated name",
        "goal_amt": 1000,
        "description": "Updated description",
        "def_lang": "es"
    })

    assert updated_response.status_code == 200
    data = updated_response.get_json()
    assert data["name"] == "updated name"
    assert data["goal_amt"] == 1000
    assert data["description"] == "Updated description"
    assert data["def_lang"] == "en"

def test_delete_campaign(client):
    create_response = client.post("/campaigns", json={
        "name": "To Be Deleted",
        "goal_amt": 2000,
        "description": "This campaign will be deleted",
        "def_lang": "en"
    })
    campaign_id = create_response.get_json()["id"]

    delete_response = client.delete(f"/campaigns/{campaign_id}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/campaigns/{campaign_id}")
    assert get_response.status_code == 404