# Architecture

## Overview

Automobile Restoration Tracker is a server-rendered Flask application. It deliberately uses a small architecture suitable for a single household, hobby shop, or restoration team.

```text
Browser
  │ HTTP
  ▼
Gunicorn / Flask
  ├── routes and HTML forms
  ├── SQLAlchemy models
  ├── Jinja templates
  └── validated image uploads
       │
       ├── SQLite database
       └── uploaded image directory
```

## Main entities

- **Project** - a vehicle and its restoration scope
- **Job** - a discrete work item, such as rebuilding brakes
- **Part** - an item to research, order, receive, and install
- **ReferenceLink** - manuals, vendors, forum posts, and videos
- **Photo** - visual evidence attached to a job
- **Expense** - money spent against a project
- **ProjectNote** - decisions, measurements, serial numbers, and lessons learned

## Design choices

SQLite keeps deployment and backup simple. The application factory makes testing and future configuration easier. Uploaded files are stored outside the image when Docker is used. Server-rendered pages avoid a separate frontend build and remain usable on workshop tablets and phones.

## Known limitations

There is no authentication, authorization, database migration framework, background queue, or object storage support. These should be addressed before public or multi-user deployment.
