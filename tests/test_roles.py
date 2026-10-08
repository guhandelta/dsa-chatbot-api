# Role gating: students are locked out of training, admins assign instructors,
# and ADMIN_EMAILS bootstraps the first admin.
import pytest
from sqlalchemy import select

from app.core.config import settings
from app.db.models import User


async def _reg(client, email, password="password123"):
    r = await client.post("/auth/register", json={"email": email, "password": password})
    return r.json()


async def test_new_user_is_student(client):
    body = await _reg(client, "s@x.com")
    assert body["user"]["role"] == "student"


async def test_admin_email_bootstraps_admin(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "boss@x.com")
    body = await _reg(client, "boss@x.com")
    assert body["user"]["role"] == "admin"


async def test_student_cannot_access_training(client):
    body = await _reg(client, "nope@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    r = await client.get("/training/status", headers=h)
    assert r.status_code == 403


async def test_student_cannot_list_users(client):
    body = await _reg(client, "curious@x.com")
    h = {"Authorization": f"Bearer {body['access_token']}"}
    assert (await client.get("/admin/users", headers=h)).status_code == 403


async def test_admin_promotes_student_to_instructor(client, monkeypatch, db):
    monkeypatch.setattr(settings, "admin_emails", "boss2@x.com")
    admin = await _reg(client, "boss2@x.com")
    student = await _reg(client, "learner@x.com")
    ah = {"Authorization": f"Bearer {admin['access_token']}"}

    r = await client.patch(
        f"/admin/users/{student['user']['id']}/role", headers=ah, json={"role": "instructor"}
    )
    assert r.status_code == 200
    assert r.json()["role"] == "instructor"

    # The promoted user can now reach the training section
    sh = {"Authorization": f"Bearer {student['access_token']}"}
    assert (await client.get("/training/status", headers=sh)).status_code == 200


async def test_admin_cannot_demote_self(client, monkeypatch):
    monkeypatch.setattr(settings, "admin_emails", "boss3@x.com")
    admin = await _reg(client, "boss3@x.com")
    ah = {"Authorization": f"Bearer {admin['access_token']}"}
    r = await client.patch(
        f"/admin/users/{admin['user']['id']}/role", headers=ah, json={"role": "student"}
    )
    assert r.status_code == 400


async def test_instructor_cannot_manage_roles(client, monkeypatch, db):
    monkeypatch.setattr(settings, "admin_emails", "boss4@x.com")
    admin = await _reg(client, "boss4@x.com")
    instructor = await _reg(client, "teach@x.com")
    ah = {"Authorization": f"Bearer {admin['access_token']}"}
    await client.patch(
        f"/admin/users/{instructor['user']['id']}/role", headers=ah, json={"role": "instructor"}
    )
    th = {"Authorization": f"Bearer {instructor['access_token']}"}
    assert (await client.get("/admin/users", headers=th)).status_code == 403
