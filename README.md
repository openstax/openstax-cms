[![OpenStax](https://img.shields.io/badge/OpenStax-Web-00A6C9?style=for-the-badge&logo=openstax&logoColor=white)](https://openstax.org)\
[![codecov](https://codecov.io/gh/openstax/openstax-cms/branch/main/graph/badge.svg?token=hHMb4KUGYC)](https://codecov.io/gh/openstax/openstax-cms)
[![CI](https://github.com/openstax/openstax-cms/actions/workflows/tests.yml/badge.svg)](https://github.com/openstax/openstax-cms/actions/workflows/tests.yml)
![](https://codebuild.us-west-2.amazonaws.com/badges?uuid=eyJlbmNyeXB0ZWREYXRhIjoiek9QM293aWxTZkdOZ0kwb00yTlZPaFJqck53RENqMFFaWGNGS2xQZFpEbThaOENrWnFUQmd2cFZIdHJoUkNFekN6Z3ozc2d3MFh6dlBaT29nNVcrM2RBPSIsIml2UGFyYW1ldGVyU3BlYyI6IklqT2p6T3NwT1pHVVVKRU0iLCJtYXRlcmlhbFNldFNlcmlhbCI6MX0%3D&branch=main)
![](https://img.shields.io/github/v/tag/openstax/openstax-cms?label=latest%20tag)


OpenStax CMS
=======================

Built using [Wagtail CMS](http://wagtail.io) on top of [Django Framework](https://www.djangoproject.com). All installation instructions assume you already have [Homebrew](http://brew.sh) installed. If you are not running on MacOSX or a Linux distribution, see the hyperlinks for dependencies.

Dependencies
=======================
* [PostgreSQL](http://www.postgresql.org) (≥ 13)  
```bash
brew install postgresql
```
* [Python](https://www.python.org/) (≥ 3.11)
* [PIP](https://github.com/pypa/pip)
```bash
brew install python3
```

Installation
=======================
Verify you have Python ≥ 3.11 installed:  
```bash
python --version
python3 --version
```

Start PostgreSQL:
```bash
brew services start postgresql
```
This will also make sure PostgreSQL service starts on boot.

Create a database (this is also a shell script), which is named as `oscms_prodcms`. However, it can be renamed as long as the change is reflected on the appropriate field in `openstax/settings/base.py`:
```bash
createdb oscms_prodcms
```

Now we can install the repository. Run the following commands line by line:

```bash
git clone https://github.com/openstax/openstax-cms
cd openstax-cms/
pip3 install -r requirements/dev.txt
```

After all the modules in requirements are installed, run the migration script:

```bash
python3 manage.py migrate
```
Now, create a superuser. Run the following command and then proceed with the instructions:

```bash
python3 manage.py createsuperuser
```

Finally, start the server:

```bash
python3 manage.py runserver
```

Testing
=======================
To test OpenStax CMS on a local device, you need to overwrite some settings. This can be streamlined by introducing `local.py` in `openstax/settings/`. Any changes on or additions to `local.py` will overwrite settings. Make copy of `local.py.example` and rename it to `local.py`:
Alternatively, and maybe more conveniently, use a `.env` file in the project root to set environmental variables.

```bash
cd openstax/settings/
cp local.py.example local.py
```

Run the tests:
```bash
python3 manage.py test --settings=openstax.settings.test
```

## Postman API Testing
To test the API, use can request access to the OpenStax Postman account.  
The collection is available [here](https://www.postman.com/openstax/workspace/cms/overview).

SQLite Support
=======================
SQLite is supported as an alternative to PostgreSQL. In order to switch to SQLite, change the `DATABASES` setting
in `openstax/settings/base.py` to use `'django.db.backends.sqlite3'`, and set `NAME` to be the full path of your database file, as you would with a regular Django project.

Docker
=======================
To run the CMS in Docker containers:

```bash
docker-compose up
```

The CMS code directory from your host machine is mounted in the `app` container at `/code`. To drop into a bash terminal in the `app` container:

```bash
docker-compose exec -e DJANGO_SETTINGS_MODULE=openstax.settings.docker app bash
```

This command has been wrapped in a tiny script:

```bash
./docker/bash
```

From within the bash shell, you can run the tests:

```bash
python3 manage.py test --keepdb
```

or pound on a specific test:

```bash
python3 manage.py test --keepdb books.tests.BookTests.test_can_create_book
```

The `--keepdb` option reuses the test database from run to run so you don't have to wait for it to recreate the database and run the migrations every time.

To debug tests, you can insert the normal `import pdb; pdb.set_trace()` lines in your code and test runs from the bash environment will show you the debugger.

API Endpoints
=======================
[View the Wiki Page](https://github.com/openstax/openstax-cms/wiki/API-Endpoints) for the list of all available API endpoints and their descriptions.

Documentation
=============
* [CMS Editing Documentation](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2193391617/CMS+Editing)
* [CMS Branching and Releases](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207219713/CMS+Branching+and+Releases)
* [CMS Pull Requests](https://openstax.atlassian.net/wiki/spaces/BIT/pages/2207252512/CMS+Pull+Requests)
