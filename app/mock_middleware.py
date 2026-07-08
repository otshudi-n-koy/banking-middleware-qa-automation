import sqlite3
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException

from pydantic import BaseModel, Field
from typing import Literal


class TransactionCreate(BaseModel):
    account_id: str
    amount: float = Field(..., gt=0)
    currency: Literal["EUR", "USD", "GBP"] = "EUR"
    type: Literal["DEBIT", "CREDIT"] = "DEBIT"
    label: str = ""

DB_PATH = Path(__file__).resolve().parent.parent / "db" / "middleware.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    schema_path = Path(__file__).resolve().parent.parent / "db" / "schema.sql"
    with get_conn() as conn:
        conn.executescript(schema_path.read_text())


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield
    # ici on mettrait un cleanup (fermeture de pool de connexions, etc.)
    # rien à faire pour SQLite dans notre cas


app = FastAPI(title="Banking Middleware (Mock)", lifespan=lifespan)


@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/accounts/{account_id}/balance")
def get_balance(account_id: str):
    with get_conn() as conn:
        row = conn.execute(
            "SELECT balance, currency FROM accounts WHERE id = ?", (account_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"account_id": account_id, "balance": row["balance"], "currency": row["currency"]}


import uuid
from datetime import datetime, timezone


@app.post("/transactions", status_code=201)
def create_transaction(payload: TransactionCreate):
    with get_conn() as conn:
        account = conn.execute(
            "SELECT * FROM accounts WHERE id = ?", (payload.account_id,)
        ).fetchone()
        if account is None:
            raise HTTPException(status_code=404, detail="Account not found")

        if payload.type == "DEBIT" and account["balance"] < payload.amount:
            raise HTTPException(status_code=422, detail="Insufficient funds")

        delta = -payload.amount if payload.type == "DEBIT" else payload.amount
        new_balance = round(account["balance"] + delta, 2)

        tx_id = f"TX-{uuid.uuid4().hex[:10].upper()}"
        created_at = datetime.now(timezone.utc).isoformat()

        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, payload.account_id)
        )
        conn.execute(
            """INSERT INTO transactions
               (id, account_id, amount, currency, type, status, label, created_at)
               VALUES (?, ?, ?, ?, ?, 'SETTLED', ?, ?)""",
            (tx_id, payload.account_id, payload.amount, payload.currency, payload.type, payload.label, created_at),
        )
        conn.commit()

    return {"id": tx_id, "account_id": payload.account_id, "amount": payload.amount, "status": "SETTLED"}


@app.get("/transactions/{tx_id}")
def get_transaction(tx_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return dict(row)


@app.post("/transactions/{tx_id}/reverse")
def reverse_transaction(tx_id: str):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="Transaction not found")
        if row["status"] == "REVERSED":
            raise HTTPException(status_code=409, detail="Transaction already reversed")

        account = conn.execute(
            "SELECT * FROM accounts WHERE id = ?", (row["account_id"],)
        ).fetchone()
        delta = row["amount"] if row["type"] == "DEBIT" else -row["amount"]
        new_balance = round(account["balance"] + delta, 2)

        conn.execute(
            "UPDATE accounts SET balance = ? WHERE id = ?", (new_balance, row["account_id"])
        )
        conn.execute("UPDATE transactions SET status = 'REVERSED' WHERE id = ?", (tx_id,))
        conn.commit()

        row = conn.execute("SELECT * FROM transactions WHERE id = ?", (tx_id,)).fetchone()
    return dict(row)