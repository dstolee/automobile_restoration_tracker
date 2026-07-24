# Development guide

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

On Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

## Commands

```bash
make test
make coverage
make lint
make format
make audit
```

## Test strategy

Tests use a temporary SQLite database and temporary upload directory. CSRF is disabled only in the test configuration. Route tests cover project creation, work items, parts, links, expenses, notes, uploads, validation, and deletion.
