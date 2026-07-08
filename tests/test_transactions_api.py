import pytest

def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "UP"}


def test_create_debit_transaction_nominal(client):
    resp = client.post(
        "/transactions",
        json={"account_id": "ACC-0001", "amount": 100.0, "type": "DEBIT", "label": "Retrait DAB"},
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["status"] == "SETTLED"
    assert body["account_id"] == "ACC-0001"

    balance = client.get("/accounts/ACC-0001/balance").json()
    assert balance["balance"] == pytest.approx(1400.00)


def test_debit_insufficient_funds_is_rejected(client):
    resp = client.post(
        "/transactions",
        json={"account_id": "ACC-0002", "amount": 99999.0, "type": "DEBIT"},
    )
    assert resp.status_code == 422
    assert "Insufficient funds" in resp.json()["detail"]


def test_transaction_on_unknown_account_returns_404(client):
    resp = client.post(
        "/transactions",
        json={"account_id": "ACC-9999", "amount": 10.0, "type": "DEBIT"},
    )
    assert resp.status_code == 404

def test_reverse_transaction_restores_balance(client):
    create = client.post(
        "/transactions",
        json={"account_id": "ACC-0001", "amount": 500.0, "type": "DEBIT", "label": "Achat"},
    )
    tx_id = create.json()["id"]

    reverse = client.post(f"/transactions/{tx_id}/reverse")
    assert reverse.status_code == 200
    assert reverse.json()["status"] == "REVERSED"

    balance = client.get("/accounts/ACC-0001/balance").json()
    assert balance["balance"] == pytest.approx(1500.00)


def test_double_reversal_is_rejected(client):
    create = client.post(
        "/transactions",
        json={"account_id": "ACC-0001", "amount": 200.0, "type": "DEBIT"},
    )
    tx_id = create.json()["id"]
    client.post(f"/transactions/{tx_id}/reverse")

    second = client.post(f"/transactions/{tx_id}/reverse")
    assert second.status_code == 409


@pytest.mark.parametrize(
    "amount,tx_type,expected_status",
    [
        (0, "DEBIT", 422),
        (-10, "CREDIT", 422),
        (1, "DEBIT", 201),
    ],
)
def test_amount_boundary_values(client, amount, tx_type, expected_status):
    resp = client.post(
        "/transactions",
        json={"account_id": "ACC-0001", "amount": amount, "type": tx_type},
    )
    assert resp.status_code == expected_status