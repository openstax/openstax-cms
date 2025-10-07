# OpenStax CMS - Claude Agent Guide

## Overview

OpenStax CMS is a content management system built with **Wagtail CMS** on top of **Django Framework**. It manages content for openstax.org including books, pages, news, and various marketing pages.

## Technology Stack

- **Framework**: Django (Python ≥ 3.11)
- **CMS**: Wagtail CMS
- **Database**: PostgreSQL (≥ 13) or SQLite
- **Language**: Python ≥ 3.11

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

1. **Clone the repository**:
   ```bash
   git clone https://github.com/openstax/openstax-cms
   cd openstax-cms/
   ```

2. **Create and start PostgreSQL database** (skip if using SQLite):
   ```bash
   # Start PostgreSQL
   brew services start postgresql

   # Create database
   createdb oscms_prodcms
   ```

3. **Install Python dependencies**:
   ```bash
   # For development
   pip3 install -r requirements/dev.txt

   # For production
   pip3 install -r requirements/production.txt

   # For testing only
   pip3 install -r requirements/test.txt
   ```

4. **Create local settings file** (REQUIRED before migrations):
   ```bash
   cd openstax/settings/
   cp local.py.example local.py
   cd ../..
   ```

   The `local.py` file overrides base settings for local development. Key settings:
   - `SECRET_KEY`: Set a secure random string
   - `DEBUG=True`: Enable debug mode
   - `DEFAULT_FILE_STORAGE`: Uses local filesystem (not S3)
   - `CORS_ORIGIN_WHITELIST`: Configure for frontend dev servers

5. **Run database migrations**:
   ```bash
   python3 manage.py migrate
   ```

6. **Create superuser** (for Wagtail admin access):
   ```bash
   python3 manage.py createsuperuser
   ```

7. **Start development server**:
   ```bash
   python3 manage.py runserver
   ```

   Access at: http://localhost:8000
   Admin at: http://localhost:8000/admin

## Creating Django Migrations

When you modify model fields in `pages/models.py` or other model files:

1. **Ensure local.py exists**:
   ```bash
   # If not already created
   cp openstax/settings/local.py.example openstax/settings/local.py
   ```

2. **Install dev requirements** (includes Django):
   ```bash
   pip3 install -r requirements/dev.txt
   ```

3. **Generate migration**:
   ```bash
   python3 manage.py makemigrations
   ```

   This creates a new migration file in the appropriate `migrations/` directory.

4. **Review the migration**:
   - Check the generated file in `pages/migrations/` (or relevant app)
   - Verify field definitions match your intent
   - Ensure migration number is sequential

5. **Test the migration**:
   ```bash
   python3 manage.py migrate
   ```

6. **Commit both model changes and migration**:
   ```bash
   git add pages/models.py pages/migrations/XXXX_*.py
   git commit -m "Add new fields to Model"
   ```

### Migration Best Practices

- **Always create local.py first** - Without it, Django may use incorrect drivers
- **Use makemigrations** - Don't write migrations manually unless necessary
- **One logical change per migration** - Keep migrations focused
- **Test migrations** - Run `migrate` locally before pushing
- **Include in PR** - Always commit migrations with model changes

## Common Development Tasks

### Running Tests

```bash
# All tests with test settings
python3 manage.py test --settings=openstax.settings.test

# Specific test
python3 manage.py test pages.tests.AssignableTests --settings=openstax.settings.test

# With test database reuse (faster)
python3 manage.py test --keepdb --settings=openstax.settings.test
```

### Using Docker

```bash
# Start containers
docker-compose up

# Access bash in app container
docker-compose exec -e DJANGO_SETTINGS_MODULE=openstax.settings.docker app bash

# Or use the helper script
./docker/bash

# Run tests in Docker
python3 manage.py test --keepdb
```

### Database Management

```bash
# Create fresh database
python3 manage.py migrate

# Reset database (caution: destroys data)
python3 manage.py flush

# Load fixtures
python3 manage.py loaddata fixtures/fixture_name.json

# Create database dump
python3 manage.py dumpdata > dump.json
```

### SQLite Alternative

To use SQLite instead of PostgreSQL:

1. Edit `openstax/settings/base.py`
2. Change `DATABASES` setting to use `'django.db.backends.sqlite3'`
3. Set `NAME` to your database file path

## Key Models

### Assignable (pages/models.py:3380)

The main landing page for the Assignable product. Key field groups:
- **Heading section**: `heading_image`, `heading_title_image`, `subheading`, `heading_description`
- **CTA buttons**: Three sets of `*_cta_header`, `*_cta_description`, `*_cta_link`, `*_cta_button_text`
  - `add_assignable_cta_*` (IT admin focused)
  - `instructor_interest_cta_*` (instructor interest)
  - `instructor_help_cta_*` (instructor help)
- **Course listings**: `available_books`, `coming_soon_books` (StreamFields)
- **Additional sections**: `section_2_*`, `faq_*`, `quote_*`, etc.

### Wagtail Concepts

- **Page models**: Inherit from `wagtail.models.Page`
- **content_panels**: Define fields shown in Wagtail admin
- **api_fields**: Define fields exposed via API
- **StreamFields**: Flexible content blocks (see `custom_blocks.py`)

## API

API endpoints documented at: https://github.com/openstax/openstax-cms/wiki/API-Endpoints

Postman collection: https://www.postman.com/openstax/workspace/cms/overview

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

### Migration conflicts

If you have migration conflicts:
```bash
# Show current migrations
python3 manage.py showmigrations

# Squash migrations (advanced)
python3 manage.py squashmigrations app_name start_migration end_migration
```

### Database connection issues

- Verify PostgreSQL is running: `brew services list`
- Check database exists: `psql -l | grep oscms`
- Verify database settings in `openstax/settings/base.py`
