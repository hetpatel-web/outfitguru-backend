def register(client):
    return client.post(
        "/auth/register",
        json={"email": "test@example.com", "password": "secret123"},
    )


def login(client):
    return client.post(
        "/auth/login",
        json={"email": "test@example.com", "password": "secret123"},
    )


def auth_headers(token: str):
    return {"Authorization": f"Bearer {token}"}


def test_register_and_login(client):
    reg = register(client)
    assert reg.status_code == 201
    token = reg.json()["token"]["access_token"]
    assert token

    log = login(client)
    assert log.status_code == 200
    assert log.json()["access_token"]


def test_create_and_list_wardrobe_items(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    create_resp = client.post(
        "/wardrobe/items",
        json={"category": "top", "color": "navy"},
        headers=auth_headers(token),
    )
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]
    assert item_id

    list_resp = client.get("/wardrobe/items", headers=auth_headers(token))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["id"] == item_id


def test_recommendation_missing_categories_returns_400(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    resp = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert resp.status_code == 400
    assert "Add at least one item" in resp.json().get("detail", "")


def test_recommendation_success_with_minimum_items(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    for cat in ["top", "bottom", "footwear"]:
        create = client.post(
            "/wardrobe/items",
            json={"category": cat, "color": f"{cat}-color"},
            headers=auth_headers(token),
        )
        assert create.status_code == 201

    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    outfit = rec.json()
    assert outfit["item_ids"] and len(outfit["item_ids"]) >= 3
    assert outfit["feedback"] == "none"
    assert outfit.get("reason")
