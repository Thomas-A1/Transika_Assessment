from datetime import timedelta

from app import storage
from app.utils import now_utc

ERROR_KEYS = {"code", "message", "details"}


def initiate(client, **changes):
    data = {
        "sender_id": "sender_001",
        "amount": 100,
        "currency": "GHS",
        "payment_method": "mobile_money",
    }
    data.update(changes)
    return client.post("/collections/initiate", json=data)


def quote(client, **changes):
    data = {"from_currency": "GHS", "to_currency": "NGN", "amount": 100}
    data.update(changes)
    return client.post("/conversions/quote", json=data)


def test_successful_collection_initiation(client):
    resp = initiate(client)

    assert resp.status_code == 201
    body = resp.json()
    assert body["collection_id"].startswith("col_")
    assert body["sender_id"] == "sender_001"
    assert body["amount"] == 100
    assert body["currency"] == "GHS"
    assert body["payment_method"] == "mobile_money"
    assert body["status"] == "pending"
    assert body["created_at"].endswith("Z")


def test_rejects_unsupported_currency(client):
    resp = initiate(client, currency="EUR")

    assert resp.status_code == 422
    body = resp.json()
    assert set(body) == ERROR_KEYS
    assert body["code"] == "unsupported_currency"
    assert body["details"]["currency"] == "EUR"
    assert "GHS" in body["details"]["supported_currencies"]


def test_valid_conversion_quote(client):
    resp = quote(client, from_currency="GHS", to_currency="NGN", amount=100)

    assert resp.status_code == 200
    body = resp.json()
    assert body["quote_id"].startswith("qte_")
    assert body["corridor"] == "GHS-NGN"
    assert body["exchange_rate"] > 0
    assert body["converted_amount"] == round(100 * body["exchange_rate"], 2)
    assert body["fee_usd"] == 1.20
    assert body["rate_expires_at"].endswith("Z")


def test_expired_quote_rejected_on_execute(client):
    quote_id = quote(client).json()["quote_id"]
    collection_id = initiate(client).json()["collection_id"]

    # Mark the collection completed so only the quote check can fail,
    # then force the quote to have already expired.
    storage.collections[collection_id]["created_at"] = now_utc() - timedelta(seconds=25)
    storage.quotes[quote_id]["rate_expires_at"] = now_utc() - timedelta(seconds=1)

    resp = client.post(
        "/conversions/execute",
        json={"quote_id": quote_id, "collection_id": collection_id},
    )

    assert resp.status_code == 409
    body = resp.json()
    assert set(body) == ERROR_KEYS
    assert body["code"] == "quote_expired"


def test_collection_not_completed_rejected_on_execute(client):
    quote_id = quote(client).json()["quote_id"]
    # A fresh collection is still "pending", so execute must be rejected.
    collection_id = initiate(client).json()["collection_id"]

    resp = client.post(
        "/conversions/execute",
        json={"quote_id": quote_id, "collection_id": collection_id},
    )

    assert resp.status_code == 409
    body = resp.json()
    assert set(body) == ERROR_KEYS
    assert body["code"] == "collection_not_completed"
    assert body["details"]["current_status"] == "pending"
    assert body["details"]["required_status"] == "completed"
