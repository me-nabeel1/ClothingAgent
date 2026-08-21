# Development & Testing Guide

## Database Initialization & Seeding

1. **Alembic Database Migration**:
   ```powershell
   $env:PYTHONPATH="clothing_app"
   alembic -c clothing_app/alembic.ini upgrade head
   ```

2. **Canonical Database Seed Script**:
   ```powershell
   $env:PYTHONPATH="clothing_app"
   python clothing_app/scripts/seed.py
   ```

---

## Running Test Suites

### 1. Commerce Backend Test Suite
```powershell
$env:PYTHONPATH="clothing_app"
pytest clothing_app/tests -q
```
*Expected: 7 passed, 1 skipped*

### 2. Fitzy Agent Test Suite (Phases 1 - 4.1)
```powershell
$env:PYTHONPATH="clothing_agent"
pytest clothing_agent/tests -q
```
*Expected: 30 passed*

---

## Running the Unified Application

Launch the single-port FastAPI unified service:

```powershell
uvicorn main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
