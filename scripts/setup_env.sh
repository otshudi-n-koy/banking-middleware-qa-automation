#!/usr/bin/env bash
set -euo pipefail

echo "==> Checking Python version"
python --version

echo "==> Creating virtual environment (.venv)"
python -m venv .venv
source .venv/Scripts/activate 2>/dev/null || source .venv/bin/activate

echo "==> Installing dependencies"
pip install --upgrade pip
pip install -r requirements.txt

echo "==> Preparing SQLite database directory"
mkdir -p db
rm -f db/middleware.db

echo "==> Environment ready. Activate with: source .venv/Scripts/activate (Windows) or source .venv/bin/activate (Linux/Mac)"