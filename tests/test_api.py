def register(client, email: str = "test@example.com"):
    return client.post(
        "/auth/register",
        json={"email": email, "password": "secret123"},
    )


def login(client, email: str = "test@example.com"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": "secret123"},
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
        json={"name": "Navy tee", "category": "top", "color": "navy"},
        headers=auth_headers(token),
    )
    assert create_resp.status_code == 201
    item_id = create_resp.json()["id"]
    assert item_id
    assert create_resp.json()["color_family"] == "Other"
    assert create_resp.json()["season"] == "All-season"
    assert create_resp.json()["subtype"] == "General"

    list_resp = client.get("/wardrobe/items", headers=auth_headers(token))
    assert list_resp.status_code == 200
    items = list_resp.json()
    assert len(items) == 1
    assert items[0]["id"] == item_id


def test_recommendation_missing_categories_returns_need_more_items(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    resp = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "need_more_items"
    assert "footwear" in data["missing_categories"]


def test_recommendation_success_with_minimum_items(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    for cat in ["top", "bottom", "footwear"]:
        create = client.post(
            "/wardrobe/items",
            json={"name": cat, "category": cat, "color": f"{cat}-color"},
            headers=auth_headers(token),
        )
        assert create.status_code == 201

    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    outfit = rec.json()
    assert outfit["item_ids"] and len(outfit["item_ids"]) >= 3
    assert outfit["feedback"] == "none"
    assert outfit.get("reason")


def test_wardrobe_categories_endpoint(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    resp = client.get("/wardrobe/categories", headers=auth_headers(token))
    assert resp.status_code == 200
    data = resp.json()
    assert "categories" in data
    assert "color_families" in data and "Black" in data["color_families"]
    assert "seasons" in data and "All-season" in data["seasons"]
    top_category = next(c for c in data["categories"] if c["slug"] == "top")
    assert "General" in top_category["subtypes"]


def test_invalid_color_family_rejected(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    resp = client.post(
        "/wardrobe/items",
        json={"category": "top", "color": "navy", "color_family": "Rainbow"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422


def test_update_preferences_requires_auth(client):
    resp = client.patch("/me/preferences", json={"goal": "daily"})
    assert resp.status_code in (401, 403)


def test_update_preferences_sets_and_clears_goal(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    update = client.patch(
        "/me/preferences",
        json={"goal": "daily"},
        headers=auth_headers(token),
    )
    assert update.status_code == 200
    assert update.json()["goal"] == "daily"

    clear = client.patch(
        "/me/preferences",
        json={"goal": None},
        headers=auth_headers(token),
    )
    assert clear.status_code == 200
    assert clear.json()["goal"] is None


def test_update_preferences_rejects_invalid_goal(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    resp = client.patch(
        "/me/preferences",
        json={"goal": "someday"},
        headers=auth_headers(token),
    )
    assert resp.status_code == 422
