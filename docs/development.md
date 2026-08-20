# Development & Testing Guide

## Prerequisites

- Python 3.11+
- Virtual environment (`.venv`) initialized with required dependencies (`requirements.txt`).

## Environment Setup

1. **Activate Virtual Environment**:
   - **Windows (PowerShell)**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
2. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

---

## Running Test Suites

### 1. Fitzy Agent Test Suite (Phases 1, 2 & 3)
```powershell
pytest clothing_agent/tests -q
```
*Expected output: `23 passed`*

### 2. Backend Domain Test Suite
```powershell
pytest tests/ -q
```
*Expected output: `3 passed, 1 skipped`*

---

## Compilation Checks

Verify Python source syntax across the entire codebase:

```powershell
python -m compileall clothing_agent
python -m compileall app
```

---

## Launching Local Server

Run the single-port FastAPI unified service locally:

```powershell
uvicorn main:app --reload --port 8000
```
- Interactive API Docs: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/health`
