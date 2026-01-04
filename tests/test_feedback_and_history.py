from datetime import datetime, timedelta

from .test_api import auth_headers, register


def _add_item(client, token, category, color):
    resp = client.post(
        "/wardrobe/items",
        json={"name": f"{category} item", "category": category, "color": color},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def test_feedback_flow(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    for cat in ["top", "bottom", "footwear"]:
        _add_item(client, token, cat, f"{cat}-color")

    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    outfit = rec.json()

    fb = client.post(
        f"/outfits/{outfit['id']}/feedback",
        headers=auth_headers(token),
        json={"feedback": "like"},
    )
    assert fb.status_code == 200
    updated = fb.json()
    assert updated["feedback"] == "like"


def test_history_order(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]

    for cat in ["top", "bottom", "footwear"]:
        _add_item(client, token, cat, f"{cat}-color")

    rec1 = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec1.status_code == 201

    rec2 = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec2.status_code == 201

    history = client.get("/outfits/history", headers=auth_headers(token))
    assert history.status_code == 200
    outfits = history.json()
    assert len(outfits) >= 2
    created = [datetime.fromisoformat(o["created_at"]) for o in outfits]
    assert created == sorted(created, reverse=True)
