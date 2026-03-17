"""Tests for order management."""
import pytest
from fastapi.testclient import TestClient

def test_create_order_insufficient_stock(client, test_product):
    resp = client.post("/api/v1/orders/", json={
        "items": [{"product_id": test_product.id, "quantity": 9999}],
        "shipping_address": {"state": "CA", "city": "SF"}
    })
    assert resp.status_code == 400
    assert "stock" in resp.json()["detail"].lower()

def test_pay_order_not_found(client):
    resp = client.post("/api/v1/orders/99999/pay")
    assert resp.status_code == 404

def test_pay_already_paid_order(client, paid_order):
    resp = client.post(f"/api/v1/orders/{paid_order.id}/pay")
    assert resp.status_code == 400
