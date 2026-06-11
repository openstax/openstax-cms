# OpenStax CMS - Claude Agent Guide

## Overview

OpenStax CMS is a content management system built with **Wagtail CMS** on top of **Django Framework**. It manages content for openstax.org including books, pages, news, and various marketing pages.

## Technology Stack

- **Framework**: Django 5.2
- **CMS**: Wagtail 7.4 (LTS)
- **Database**: PostgreSQL (≥ 13) or SQLite
- **Language**: Python ≥ 3.11 (project virtualenv runs 3.14)

## Local Environment (IMPORTANT)

This project uses a **virtualenv** — always work inside it. Do **not** use the
system/Homebrew Python (it is externally managed; `pip install` is blocked there).

```bash
workon openstax-cms          # virtualenvwrapper; venv lives at ~/.virtualenvs/openstax-cms
```

Run every `python manage.py …`, `pip install`, and test command inside that venv.
If `workon` isn't available, activate directly:
`source ~/.virtualenvs/openstax-cms/bin/activate`.

### Running tests

```bash
python manage.py test --settings=openstax.settings.test            # full suite
python manage.py test authoring --settings=openstax.settings.test
```

Add `--noinput` if a leftover `test_oscms_test` DB blocks a run, or `--keepdb` to
reuse the test DB between runs. CI installs `requirements/test.txt` and runs
`manage.py test --settings=openstax.settings.test`.

## Project Structure

```
openstax-cms/
├── pages/              # Core page models (Assignable, Book pages, etc.)
│   ├── models.py       # All Wagtail page type definitions
│   ├── migrations/     # Django migrations
│   └── custom_blocks.py # StreamField blocks
├── books/              # Book-specific models and logic
├── news/               # News/blog functionality
├── errata/             # Errata submission and management
├── accounts/           # Account-related functionality
├── api/                # API endpoints
├── openstax/           # Project settings
│   └── settings/       # Environment-specific settings
│       ├── base.py     # Base settings
│       ├── local.py.example # Local dev settings template
│       ├── test.py     # Test settings
│       └── docker.py   # Docker settings
├── requirements/       # Python dependencies
│   ├── base.txt        # Core requirements
│   ├── dev.txt         # Development requirements
│   ├── test.txt        # Test requirements
│   └── production.txt  # Production requirements
└── manage.py           # Django management script
```

## Setup Instructions

### Prerequisites

- Python ≥ 3.11
- PostgreSQL ≥ 13 (or use SQLite for development)
- pip (Python package manager)

### Installation Steps

1. **Clone the repository**
2. **Activate the virtualenv** (`workon openstax-cms`)
3. **Install Python dependencies from requirements/dev.txt**
4. **Create local settings file** (REQUIRED before migrations): `cp openstax/settings/local.py.example openstax/settings/local.py`

## Creating Django Migrations

When you modify model fields in `pages/models.py` or other model files:

1. **Ensure openstax/settings/local.py exists**
2. **Install dev requirements**
3. **Generate migration**:
   ```bash
   python3 manage.py makemigrations
   ```

   This creates a new migration file in the appropriate `migrations/` directory.

4. **Review the migration**
5. **Commit both model changes and migration**

### Migration Best Practices

- **Always create local.py first** - Without it, Django may use incorrect drivers
- **Use makemigrations** - Don't write migrations manually
- **One logical change per migration** - Keep migrations focused
- **Include in PR** - Always commit migrations with model changes

## Wagtail Concepts

- **Page models**: Inherit from `wagtail.models.Page`
- **content_panels**: Define fields shown in Wagtail admin
- **api_fields**: Define fields exposed via API
- **StreamFields**: Flexible content blocks (see `custom_blocks.py`)

## API

API endpoints documented at: https://github.com/openstax/openstax-cms/wiki/API-Endpoints

Postman collection: https://www.postman.com/openstax/workspace/cms/overview

## Headless Authoring & Draft-Save API

This branch adds an authenticated path for an AI agent (and, soon, an in-CMS MCP
server) to create/update `FlexPage`s as **unpublished drafts** — it **never
publishes** (a human reviews and publishes in the Wagtail admin).

- **Endpoint:** `POST /apps/cms/api/v2/pages/flex/` (create) and
  `PATCH /apps/cms/api/v2/pages/flex/<id>/` (update). Token-auth fast-path
  (`rest_framework.authtoken`); the global API stays public-read (`AllowAny`) — the
  write view sets its own auth/permission classes.
- **App:** everything lives in the `authoring/` app (kept out of `pages`, which
  is already the most complex app). The page models themselves stay in `pages`.
- **Service layer (surface-agnostic; the MCP tools will reuse it):**
  - `authoring/drafts.py` — validate `layout`/`body` against the real block defs,
    `create_flex_draft` / `update_flex_draft` (draft revisions only), rich-text
    reference validation, page-lock check.
  - `authoring/routing_rules.py` — reserved slugs, `RootPage`-only parents, **tree-global**
    slug uniqueness (FlexPage URLs flatten to `/<slug>`).
  - `authoring/permissions.py` — `CanDraftFlexPages` (staff + Wagtail page perms).
  - `authoring/views.py` — the DRF view; routes in `authoring/urls.py`, included
    from `openstax/urls.py` under `/apps/cms/api/v2/pages/flex/`.
  - Tests: `authoring/tests/`.
- **Contract for clients:** `docs/api/flex-draft-save.md`.
- **Design & plans (not committed; local `docs/superpowers/`):** the headless +
  AI-authoring spec and the in-CMS MCP server plan (`django-mcp-server` +
  `django-oauth-toolkit` + DCR) live there.

Wagtail 7.4 note: prefer **deferred validation** for draft saves (required-field
checks happen at publish time) and `ImageRenditionField` for headless images.

## Additional Documentation

- [CMS Editing Documentation](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2193391617/CMS+Editing)
- [CMS Branching and Releases](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207219713/CMS+Branching+and+Releases)
- [CMS Pull Requests](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207252512/CMS+Pull+Requests)

## Troubleshooting

### Import errors with botocore.vendored

If you see: `ModuleNotFoundError: No module named 'botocore.vendored'`

**Cause**: The `django_ses` package in `INSTALLED_APPS` requires botocore, which changed in newer versions.

**Solution**: This is expected in local development. The error occurs because production uses SES for email, but local development doesn't need it. Your `local.py` file should already handle this, but if needed:

```python
# In openstax/settings/local.py
from .base import INSTALLED_APPS

# Remove django_ses from INSTALLED_APPS
INSTALLED_APPS = tuple(app for app in INSTALLED_APPS if app != 'django_ses')
```
