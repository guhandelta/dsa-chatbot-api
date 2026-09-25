# Auth flow: registration grants the signup bonus, login issues a working
# token, /me reflects the balance, and protected routes reject anonymity.
async def test_register_grants_signup_bonus(client):
    r = await client.post("/auth/register", json={"email": "u@x.com", "password": "password123"})
    assert r.status_code == 201
    body = r.json()
    assert body["user"]["peppercorns"] == 50
    assert body["access_token"]


async def test_duplicate_email_rejected(client):
    await client.post("/auth/register", json={"email": "dup@x.com", "password": "password123"})
    r = await client.post("/auth/register", json={"email": "dup@x.com", "password": "password123"})
    assert r.status_code == 409


async def test_login_and_me(client):
    await client.post("/auth/register", json={"email": "me@x.com", "password": "password123"})
    r = await client.post("/auth/login", json={"email": "me@x.com", "password": "password123"})
    assert r.status_code == 200
    token = r.json()["access_token"]

    me = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.status_code == 200
    assert me.json()["email"] == "me@x.com"
    assert me.json()["peppercorns"] == 50


async def test_login_wrong_password(client):
    await client.post("/auth/register", json={"email": "w@x.com", "password": "password123"})
    r = await client.post("/auth/login", json={"email": "w@x.com", "password": "wrongpass1"})
    assert r.status_code == 401


async def test_protected_route_requires_token(client):
    r = await client.get("/auth/me")
    assert r.status_code == 401
