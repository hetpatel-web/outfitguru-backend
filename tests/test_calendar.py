from datetime import date, timedelta

from .test_api import auth_headers, register


def _add_item(client, token, category, color):
    resp = client.post(
        "/wardrobe/items",
        json={"name": f"{category} item", "category": category, "color": color},
        headers=auth_headers(token),
    )
    assert resp.status_code == 201
    return resp.json()["id"]


def _seed_outfit(client, token):
    for cat in ["top", "bottom", "footwear"]:
        _add_item(client, token, cat, f"{cat}-color")
    rec = client.post("/outfits/recommendation", headers=auth_headers(token))
    assert rec.status_code == 201
    return rec.json()


def test_calendar_requires_auth(client):
    resp = client.get("/calendar/month?year=2024&month=1")
    assert resp.status_code in (401, 403)


def test_plan_tomorrow_is_idempotent(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]
    outfit = _seed_outfit(client, token)

    tomorrow = date.today() + timedelta(days=1)
    first = client.post("/calendar/plan-tomorrow", headers=auth_headers(token))
    assert first.status_code == 200
    first_data = first.json()
    assert first_data["date"] == tomorrow.isoformat()
    assert first_data["outfit_id"] == outfit["id"]
    assert first_data["status"] == "planned"

    second = client.post("/calendar/plan-tomorrow", headers=auth_headers(token))
    assert second.status_code == 200
    assert second.json()["id"] == first_data["id"]

    day_resp = client.get(f"/calendar/day?date={tomorrow.isoformat()}", headers=auth_headers(token))
    assert day_resp.status_code == 200
    day_data = day_resp.json()["occurrence"]
    assert day_data["outfit_id"] == outfit["id"]

    month_resp = client.get(
        f"/calendar/month?year={tomorrow.year}&month={tomorrow.month}", headers=auth_headers(token)
    )
    assert month_resp.status_code == 200
    dates = [entry["date"] for entry in month_resp.json()["occurrences"]]
    assert tomorrow.isoformat() in dates


def test_confirm_worn_updates_status_and_reason(client):
    reg = register(client)
    token = reg.json()["token"]["access_token"]
    today = date.today()

    skip_resp = client.post(
        "/calendar/confirm-worn",
        json={"date": today.isoformat(), "worn": False, "negative_reason": "Plans changed"},
        headers=auth_headers(token),
    )
    assert skip_resp.status_code == 200
    skip_data = skip_resp.json()
    assert skip_data["status"] == "worn"
    assert skip_data["negative_reason"] == "Plans changed"

    worn_resp = client.post(
        "/calendar/confirm-worn",
        json={"date": today.isoformat(), "worn": True},
        headers=auth_headers(token),
    )
    assert worn_resp.status_code == 200
    worn_data = worn_resp.json()
    assert worn_data["status"] == "worn"
    assert worn_data["negative_reason"] is None
