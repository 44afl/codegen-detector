#!/bin/bash
# Non-Functional Testing Script for Code Generation Detector
# Runs security scanning, linting, and code quality checks

echo ""
echo "========================================"
echo "Non-Functional Testing Suite"
echo "========================================"
echo ""

PASSED=0
FAILED=0

# 1. Ruff Linting Check
echo "[1/5] Running Ruff Linting Check..."
poetry run ruff check . --exclude venv,.venv,client
if [ $? -eq 0 ]; then
    echo "✓ Ruff check passed"
    ((PASSED++))
else
    echo "✗ Ruff check failed"
    ((FAILED++))
fi
echo ""

# 2. Bandit Security Scan
echo "[2/5] Running Bandit Security Analysis..."
poetry run bandit -r . -ll --exclude ./venv,./client,./tests -f json -o bandit-report.json
if [ $? -eq 0 ]; then
    echo "✓ Bandit scan completed"
    ((PASSED++))
else
    echo "✗ Bandit scan found issues (see bandit-report.json)"
    ((FAILED++))
fi
echo ""

# 3. Safety Dependency Check
echo "[3/5] Running Safety Dependency Vulnerability Check..."
poetry run safety check --json
if [ $? -eq 0 ]; then
    echo "✓ Safety check passed"
    ((PASSED++))
else
    echo "✗ Safety check found vulnerabilities"
    ((FAILED++))
fi
echo ""

# 4. Pip-audit Vulnerability Scan
echo "[4/5] Running Pip-Audit Vulnerability Scan..."
poetry run pip-audit
if [ $? -eq 0 ]; then
    echo "✓ Pip-audit passed"
    ((PASSED++))
else
    echo "⚠ Pip-audit found issues (may need updating dependencies)"
    ((FAILED++))
fi
echo ""

# 5. Ruff Format Check
echo "[5/5] Running Ruff Format Check..."
poetry run ruff format . --exclude venv,.venv,client --check
if [ $? -eq 0 ]; then
    echo "✓ Code formatting is correct"
    ((PASSED++))
else
    echo "⚠ Code formatting issues found (run: ruff format .)"
    ((FAILED++))
fi
echo ""

# Print summary
echo "========================================"
echo "Test Summary"
echo "========================================"
echo "Passed: $PASSED/5"
echo "Failed: $FAILED/5"
echo ""

if [ $FAILED -gt 0 ]; then
    echo "Some tests failed. Review the output above."
    exit 1
else
    echo "All non-functional tests passed!"
    exit 0
fi
