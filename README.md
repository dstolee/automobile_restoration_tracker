# Automobile Restoration Tracker

[![CI](https://github.com/YOUR-GITHUB-USERNAME/automobile-restoration-tracker/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR-GITHUB-USERNAME/automobile-restoration-tracker/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue.svg)](pyproject.toml)

A self-hosted Flask application for organizing an automobile restoration from first inspection through completed build. It keeps work plans, parts research, reference links, photographs, expenses, measurements, and lessons learned together by vehicle and job.

> **Security note:** authentication is not yet implemented. Keep the application on a trusted LAN or behind a VPN. Do not expose it directly to the public internet.

## Features

- Multiple vehicle projects with dashboard cover photos, scope, target date, status, and completion percentage
- Work items categorized by vehicle system, priority, state, deadline, time, and estimated cost
- Parts lists with supplier links, part numbers, order status, costs, storage locations, and related jobs
- Per-job photo logs for before, progress, problem, reference, and after photographs
- Reference library for manuals, forum discussions, specifications, videos, and vendors
- Expense tracking and project spending totals
- Notes for measurements, paint codes, serial numbers, inspections, decisions, and lessons learned
- Responsive server-rendered interface suited to a phone or tablet in the garage
- SQLite and local photo storage for simple self-hosting and backup
- Docker Compose deployment, health check, tests, linting, and CI

## Quick start with Docker Desktop or Docker Engine

```bash
git clone https://github.com/YOUR-GITHUB-USERNAME/automobile-restoration-tracker.git
cd automobile-restoration-tracker
cp .env.example .env
# Edit .env and replace SECRET_KEY
docker compose up -d --build
```

Open `http://localhost:5000` or `http://SERVER-IP:5000`.

Application data is persisted in:

```text
data/restoration.db
data/uploads/
```

## Windows PowerShell

```powershell
git clone https://github.com/YOUR-GITHUB-USERNAME/automobile-restoration-tracker.git
cd automobile-restoration-tracker
Copy-Item .env.example .env
notepad .env
docker compose up -d --build
Start-Process http://localhost:5000
```

## Local Python development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pytest
flask --app run.py --debug run
```

Windows PowerShell activation:

```powershell
.venv\Scripts\Activate.ps1
```

## Quality checks

```bash
ruff check .
ruff format --check .
pytest --cov=app --cov-report=term-missing
pip-audit
```

GitHub Actions runs linting and tests on Python 3.11, 3.12, and 3.13 and verifies that the Docker image builds.

## Repository map

```text
app/                    Flask application, models, routes, templates, and CSS
docs/                   Architecture, deployment, development, and backups
tests/                  Pytest application and workflow tests
.github/                CI, security audit, issue forms, and Dependabot
scripts/backup.sh       Simple persistent-data backup helper
config.py               Runtime configuration
run.py                  WSGI entry point
Dockerfile              Production container image
docker-compose.yml      Self-hosted deployment
pyproject.toml          Package metadata and tool configuration
```

## Documentation

- [Architecture](docs/architecture.md)
- [Deployment](docs/deployment.md)
- [Development](docs/development.md)
- [Backup and restore](docs/backup-and-restore.md)
- [Contributing](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Changelog](CHANGELOG.md)

## Roadmap

Likely future work includes authentication and roles, Alembic migrations, PostgreSQL, CSV import/export, a Kanban view, printable restoration books, receipt attachments, EXIF date extraction, QR labels for parts bins, tool inventory, and maintenance records after restoration.

## License

Released under the [MIT License](LICENSE).
