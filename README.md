# Banking Middleware — QA Automation Demo

A self-contained QA automation project simulating **integration testing of a
banking back-end/middleware transaction gateway** — built to demonstrate the
exact stack requested for Senior QA Automation missions in banking (Python,
SQL, Linux, Jenkins/CI-CD, AWS).

## What's under test

`app/mock_middleware.py` is a small FastAPI service standing in for a real
banking middleware: create debit/credit transactions, check account
balances, reverse transactions — backed by SQLite.

## Stack demonstrated

| Requirement | Where |
|---|---|
| **Tests d'intégration back-end/middleware** | `tests/test_transactions_api.py` |
| **Automatisation en Python** | pytest, fixtures, parametrization |
| **SQL** | `db/schema.sql`, `tests/test_sql_data_integrity.py` — réconciliation grand-livre/solde |
| **Linux** | `scripts/setup_env.sh`, `scripts/run_tests.sh` |
| **Jenkins / CI-CD** | `Jenkinsfile` — pipeline déclaratif |
| **AWS** | `tests/test_aws_s3_reports.py` (S3 mocké via moto) |

## Running locally

\`\`\`bash
./scripts/setup_env.sh
source .venv/Scripts/activate
./scripts/run_tests.sh
\`\`\`

Reports land in `./reports` (JUnit XML, self-contained HTML, coverage XML).