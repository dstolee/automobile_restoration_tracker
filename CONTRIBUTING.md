# Contributing

Thank you for helping improve Automobile Restoration Tracker.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate        # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements-dev.txt
pytest
```

Run the development server with:

```bash
flask --app run.py --debug run
```

## Before opening a pull request

```bash
ruff check .
ruff format --check .
pytest --cov=app --cov-report=term-missing
```

Please add tests for new behavior, update documentation when configuration or user-visible behavior changes, and keep pull requests focused.

## Commit and pull request guidance

Use concise imperative commit subjects, such as `Add supplier filtering`. In the pull request, explain the problem, the approach, testing performed, screenshots for interface changes, and any migration or deployment impact.

## Reporting security problems

Do not open a public issue for a vulnerability. Follow [SECURITY.md](SECURITY.md).
