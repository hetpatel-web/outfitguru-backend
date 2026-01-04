from datetime import datetime

from .test_api import auth_headers, register


def _add_item(client, token, category, color):
    resp = client.post(
        "/wardrobe/items",
        json={"name": f"{category} item", "category": category, "color": color},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_recommendation_avoids_repeating_last_outfit(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    # Two options per required category
    top1 = _add_item(client, token, "top", "navy")
    top2 = _add_item(client, token, "top", "black")
    bottom1 = _add_item(client, token, "bottom", "grey")
    bottom2 = _add_item(client, token, "bottom", "olive")
    foot1 = _add_item(client, token, "footwear", "white")
    foot2 = _add_item(client, token, "footwear", "gum")

    first = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert first.status_code == 201
    first_ids = set(first.json()["item_ids"])

    second = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert second.status_code == 201
    second_ids = set(second.json()["item_ids"])

    assert first_ids != second_ids  # should not repeat immediately when alternatives exist


def test_recommendation_includes_reason(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    for cat in ["top", "bottom", "footwear"]:
        _add_item(client, token, cat, f"{cat}-color")

    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    data = rec.json()
    assert data.get("reason")


def test_recommendation_can_use_one_piece_without_bottom(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    one_piece_id = _add_item(client, token, "one_piece", "black")
    footwear_id = _add_item(client, token, "footwear", "white")

    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    data = rec.json()
    item_ids = data["item_ids"]
    wardrobe = {item["id"]: item["category"] for item in client.get("/wardrobe/items", headers=auth_headers(token)).json()}
    assert one_piece_id in item_ids
    assert footwear_id in item_ids
    assert all(wardrobe[item_id] != "bottom" for item_id in item_ids)
