from .test_api import auth_headers, register


def test_full_crud_flow(client):
  reg = register(client)
  token = reg.json()["token"]["access_token"]

  # create
  create = client.post(
      "/wardrobe/items",
      json={
          "name": "Warm sweater",
          "category": "top",
          "subtype": "Sweater",
          "color": "charcoal",
          "color_family": "Grey",
          "season": "Cold",
      },
      headers=auth_headers(token),
  )
  assert create.status_code == 201
  item_id = create.json()["id"]

  # list
  listed = client.get("/wardrobe/items?category=top&q=sweater", headers=auth_headers(token))
  assert listed.status_code == 200
  assert any(item["id"] == item_id for item in listed.json())

  # get
  detail = client.get(f"/wardrobe/items/{item_id}", headers=auth_headers(token))
  assert detail.status_code == 200
  assert detail.json()["name"] == "Warm sweater"

  # update
  update = client.patch(
      f"/wardrobe/items/{item_id}",
      json={"name": "Warm wool sweater", "subtype": "General"},
      headers=auth_headers(token),
  )
  assert update.status_code == 200
  assert update.json()["name"] == "Warm wool sweater"
  assert update.json()["subtype"] == "General"

  # delete
  delete = client.delete(f"/wardrobe/items/{item_id}", headers=auth_headers(token))
  assert delete.status_code == 204

  missing = client.get(f"/wardrobe/items/{item_id}", headers=auth_headers(token))
  assert missing.status_code == 404


def test_invalid_subtype_rejected(client):
  reg = register(client)
  token = reg.json()["token"]["access_token"]

  resp = client.post(
      "/wardrobe/items",
      json={"name": "Odd item", "category": "top", "subtype": "Boots", "color": "red"},
      headers=auth_headers(token),
  )
  assert resp.status_code == 422


def test_user_cannot_access_others_items(client):
  reg1 = register(client, email="one@example.com")
  token1 = reg1.json()["token"]["access_token"]
  reg2 = register(client, email="two@example.com")
  token2 = reg2.json()["token"]["access_token"]

  item_resp = client.post(
      "/wardrobe/items",
      json={"name": "Private item", "category": "top", "color": "black"},
      headers=auth_headers(token1),
  )
  item_id = item_resp.json()["id"]

  other = client.get(f"/wardrobe/items/{item_id}", headers=auth_headers(token2))
  assert other.status_code == 404


def test_delete_blocked_when_used_in_outfit(client):
  reg = register(client)
  token = reg.json()["token"]["access_token"]

  top = client.post("/wardrobe/items", json={"name": "Top", "category": "top", "color": "blue"}, headers=auth_headers(token)).json()["id"]
  bottom = client.post("/wardrobe/items", json={"name": "Bottom", "category": "bottom", "color": "grey"}, headers=auth_headers(token)).json()["id"]
  shoe = client.post("/wardrobe/items", json={"name": "Shoe", "category": "footwear", "color": "white"}, headers=auth_headers(token)).json()["id"]

  rec = client.post("/outfits/recommendation", headers=auth_headers(token))
  assert rec.status_code == 201

  delete_attempt = client.delete(f"/wardrobe/items/{top}", headers=auth_headers(token))
  assert delete_attempt.status_code == 409
