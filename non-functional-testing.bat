@echo off
REM Non-Functional Testing Script for Code Generation Detector
REM Runs security scanning, linting, and code quality checks

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Non-Functional Testing Suite
echo ========================================
echo.

REM Counter for tracking results
set /a PASSED=0
set /a FAILED=0

REM 1. Ruff Linting Check
echo [1/5] Running Ruff Linting Check...
poetry run ruff check . --exclude venv,.venv,client
if !errorlevel! equ 0 (
    echo ✓ Ruff check passed
    set /a PASSED+=1
) else (
    echo ✗ Ruff check failed
    set /a FAILED+=1
)
echo.

REM 2. Bandit Security Scan
echo [2/5] Running Bandit Security Analysis...
poetry run bandit -r . -ll --exclude ./venv,./client,./tests -f json -o bandit-report.json
if !errorlevel! equ 0 (
    echo ✓ Bandit scan completed
    set /a PASSED+=1
) else (
    echo ✗ Bandit scan found issues ^(see bandit-report.json^)
    set /a FAILED+=1
)
echo.

REM 3. Safety Dependency Check
echo [3/5] Running Safety Dependency Vulnerability Check...
poetry run safety check --json
if !errorlevel! equ 0 (
    echo ✓ Safety check passed
    set /a PASSED+=1
) else (
    echo ✗ Safety check found vulnerabilities
    set /a FAILED+=1
)
echo.

REM 4. Pip-audit Vulnerability Scan
echo [4/5] Running Pip-Audit Vulnerability Scan...
poetry run pip-audit
if !errorlevel! equ 0 (
    echo ✓ Pip-audit passed
    set /a PASSED+=1
) else (
    echo ⚠ Pip-audit found issues ^(may need updating dependencies^)
    set /a FAILED+=1
)
echo.

REM 5. Ruff Format Check
echo [5/5] Running Ruff Format Check...
poetry run ruff format . --exclude venv,.venv,client --check
if !errorlevel! equ 0 (
    echo ✓ Code formatting is correct
    set /a PASSED+=1
) else (
    echo ⚠ Code formatting issues found ^(run: ruff format .^)
    set /a FAILED+=1
)
echo.

REM Print summary
echo ========================================
echo Test Summary
echo ========================================
echo Passed: !PASSED!/5
echo Failed: !FAILED!/5
echo.

if !FAILED! gtr 0 (
    echo Some tests failed. Review the output above.
    exit /b 1
) else (
    echo All non-functional tests passed!
    exit /b 0
)
