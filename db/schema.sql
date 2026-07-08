DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS accounts;

CREATE TABLE accounts (
    id          TEXT PRIMARY KEY,
    holder_name TEXT NOT NULL,
    balance     REAL NOT NULL DEFAULT 0,
    currency    TEXT NOT NULL DEFAULT 'EUR'
);

CREATE TABLE transactions (
    id          TEXT PRIMARY KEY,
    account_id  TEXT NOT NULL REFERENCES accounts(id),
    amount      REAL NOT NULL,
    currency    TEXT NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('DEBIT', 'CREDIT')),
    status      TEXT NOT NULL CHECK (status IN ('SETTLED', 'REVERSED')),
    label       TEXT,
    created_at  TEXT NOT NULL
);

INSERT INTO accounts (id, holder_name, balance, currency) VALUES
    ('ACC-0001', 'Jean Dupont', 1500.00, 'EUR'),
    ('ACC-0002', 'Fatou Diallo', 320.50, 'EUR');