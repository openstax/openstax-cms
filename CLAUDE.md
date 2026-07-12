# OpenStax CMS - Claude Agent Guide

## Overview

OpenStax CMS is a **Wagtail** CMS on **Django** managing content for openstax.org
(books, flex/marketing pages, news, errata). It runs headless: the public site is
the `os-webview` SPA consuming this CMS's API. In deployed environments nginx only
routes `/apps/cms/api*` (plus `/admin`, docs, etc.) to Django — any SPA-facing
endpoint must live under `/apps/cms/api/`.

## Technology Stack

- **Django 6.0** / **Wagtail 7.4 (LTS)** / DRF — exact pins in `requirements/base.txt`
- **Database**: PostgreSQL (≥ 13); SQLite works for light local dev
- **Python** ≥ 3.11 (project virtualenv runs 3.14)

## Local Environment (IMPORTANT)

This project uses a **virtualenv** — always work inside it. Do **not** use the
system/Homebrew Python (it is externally managed; `pip install` is blocked there).

```bash
workon openstax-cms          # virtualenvwrapper; venv lives at ~/.virtualenvs/openstax-cms
```

Run every `python manage.py …`, `pip install`, and test command inside that venv.
If `workon` isn't available, activate directly:
`source ~/.virtualenvs/openstax-cms/bin/activate`.

Setup, once in the venv:

1. `pip install -r requirements/dev.txt` (the venv can lag the pins — re-run after dependency bumps)
2. `cp openstax/settings/local.py.example openstax/settings/local.py` — **required before any `manage.py` command**, including migrations

### Running tests

```bash
python manage.py test --settings=openstax.settings.test            # full suite
python manage.py test authoring --settings=openstax.settings.test  # one app
```

Add `--noinput` if a leftover `test_oscms_test` DB blocks a run, or `--keepdb` to
reuse the test DB between runs. CI installs `requirements/test.txt` and runs
`manage.py test --settings=openstax.settings.test`.

## Project Structure

```
pages/               Core Wagtail page models
  models/            Themed modules — ALWAYS import from pages.models, never submodules
    core.py          RootPage, FlexPage, HomePage, GeneralPage
    constants.py     Shared StreamField block-list constants
    bases.py         Concrete MTI base models (Quote, Institutions, Group)
    …                about, giving, legal, support, partners, marketing, subjects, k12
  custom_blocks.py / shared_blocks.py / table_block.py   StreamField blocks
books/               Book pages, resources, book detail API
news/                Blog (articles, collections, press)
errata/              Errata submission + admin workflow
salesforce/          Salesforce sync (Salesforce is the system of record)
api/                 Misc API endpoints (footer, mail, customization requests, …)
authoring/           Token-authed draft-save API for FlexPages — creates/updates
                     unpublished drafts only, never publishes
ai_assist/           wagtail-ai integration (agent/panel patches, prompts)
oxmenus/             CMS-driven navigation menus
oxauth/              OpenStax Accounts SSO integration
snippets/            Shared Wagtail snippets (subjects, roles, …)
global_settings/     Wagtail site settings
donations/ webinars/ mail/ redirects/ accounts/ shared/ versions/ wagtailimportexport/
openstax/settings/   base.py, local.py(.example), test.py, docker.py
requirements/        base / dev / test / production pins
docs/                Runbooks & design docs (refresh-from-prod, wagtail-transfer
                     page sync, API contracts under docs/api/)
```

## Migrations

- `openstax/settings/local.py` must exist first (wrong DB driver otherwise)
- Generate with `python manage.py makemigrations` — don't write migrations by hand
- One logical change per migration; commit the migration with the model change

## Wagtail Concepts

- **Page models**: inherit from `wagtail.models.Page`
- **content_panels**: fields shown in the Wagtail admin
- **api_fields**: fields exposed via the API
- **StreamFields**: flexible content blocks (see `pages/custom_blocks.py`)

## References

- [API endpoints wiki](https://github.com/openstax/openstax-cms/wiki/API-Endpoints) · [Postman collection](https://www.postman.com/openstax/workspace/cms/overview)
- Confluence: [CMS Editing](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2193391617/CMS+Editing) · [Branching & Releases](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207219713/CMS+Branching+and+Releases) · [Pull Requests](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207252512/CMS+Pull+Requests)

`AGENTS.md` is the same guide for other agents — keep the two in sync when editing.
