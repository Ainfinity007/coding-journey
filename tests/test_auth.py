"""Tests for authentication endpoints."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

def test_login_invalid_credentials(client):
    resp = client.post("/api/v1/auth/login", json={"email": "bad@test.com", "password": "wrong"})
    assert resp.status_code == 401

def test_login_success(client, test_user):
    resp = client.post("/api/v1/auth/login", json={"email": test_user.email, "password": "testpassword"})
    assert resp.status_code == 200
    assert "access_token" in resp.json()

def test_refresh_without_cookie(client):
    resp = client.post("/api/v1/auth/refresh")
    assert resp.status_code == 401
