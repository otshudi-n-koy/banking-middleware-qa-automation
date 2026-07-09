#!/usr/bin/env bash
set -euo pipefail

mkdir -p reports

pytest tests/ \
  -v \
  --junitxml=reports/junit.xml \
  --html=reports/report.html --self-contained-html \
  --cov=app --cov-report=xml:reports/coverage.xml --cov-report=term-missing

echo "==> Reports generated in ./reports"