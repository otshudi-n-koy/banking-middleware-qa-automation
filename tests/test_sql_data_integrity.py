def test_seed_accounts_are_present(client, sql_conn):
    rows = sql_conn.execute("SELECT id FROM accounts ORDER BY id").fetchall()
    ids = [r["id"] for r in rows]
    assert ids == ["ACC-0001", "ACC-0002"]


def test_transaction_ledger_reconciles_with_balance(client, sql_conn):
    """Après une séquence d'opérations, le solde du compte doit être égal à :
    solde initial + somme(CREDIT) - somme(DEBIT) sur les transactions SETTLED.
    Un test de rapprochement (reconciliation) classique en QA bancaire."""
    client.post("/transactions", json={"account_id": "ACC-0001", "amount": 200, "type": "DEBIT"})
    client.post("/transactions", json={"account_id": "ACC-0001", "amount": 50, "type": "CREDIT"})

    seed_balance = 1500.00
    ledger = sql_conn.execute(
        """SELECT type, SUM(amount) as total FROM transactions
           WHERE account_id = 'ACC-0001' AND status = 'SETTLED'
           GROUP BY type"""
    ).fetchall()
    movement = {row["type"]: row["total"] for row in ledger}
    expected_balance = seed_balance - movement.get("DEBIT", 0) + movement.get("CREDIT", 0)

    actual_balance = sql_conn.execute(
        "SELECT balance FROM accounts WHERE id = 'ACC-0001'"
    ).fetchone()["balance"]

    assert round(actual_balance, 2) == round(expected_balance, 2)