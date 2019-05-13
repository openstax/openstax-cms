[![Build Status](https://travis-ci.org/openstax/openstax-cms.svg?branch=master)](https://travis-ci.org/openstax/openstax-cms)
[![codecov](https://codecov.io/gh/openstax/openstax-cms/branch/master/graph/badge.svg)](https://codecov.io/gh/openstax/openstax-cms)

OpenStax CMS
=======================

Built using [Wagtail CMS](http://wagtail.io) on top of [Django Framework](https://www.djangoproject.com). All installation instructions assume you already have [Homebrew](http://brew.sh) installed. If you are not running on MacOSX or a Linux distribution, see the hyperlinks for dependencies.

Dependencies
=======================
* [PostgreSQL](http://www.postgresql.org) (≥ 11.3)  
```bash
brew install postgresql
```
* [Python](https://www.python.org/) (≥ 3.4)
* [PIP](https://github.com/pypa/pip) (≥ 8.0.0)
```bash
brew install python3
```

Installation
=======================
Verify you have Python ≥ 3.4 installed:  
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
Now, create a super user. Run the following command and then proceed with the instructions:

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
```bash
cd openstax/settings/
cp local.py.example local.py
```

Start the server:
```bash
python3 manage.py test --liveserver=localhost:8001 --settings=openstax.settings.dev
```

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
`/apps/cms/api/v2` - Wagtails API. This serves things like pages, images, and documents - except when it doesn't, see below for exceptions.

`/apps/cms/api/v2/pages` (mostly used with `/api/v2/pages/?slug=[slug]`) returns the `detail_url` for the page content. You can also call `/api/v2/pages` and get a list of all pages with their `detail_url` and `slug`.

 `/apps/cms/api/snippets/roles` - Returns list of available roles for a user. This lives in the `snippets` directory.

 `/apps/cms/api/sticky` - Returns the text for the sticky note. Lives in the `api` directory.

 `/apps/cms/api/footer` - Returns the text for the footer. Lives in the `api` directory.

 `/apps/cms/api/errata/[id]` - Returns details for a piece of Errata

 `/apps/cms/api/books` - Returns a list of books, with their slug and some information needed to render the subjects page

 `/apps/cms/api/mail/send_mail` - Takes post parameters and sends mail through Amazon SES. We prevent spamming by only having a limited set of subjects that it will accept and go to a particular email address.

 `/apps/cms/api/documents` - Custom API endpoint to return all documents with their cloudfront url, this lives in the `api` directory

 `/apps/cms/api/images` - Custom API endpoint to return all images with their cloudfront url, this lives in the `api` directory.

 `/apps/cms/api/progress` - Custom API endpoint that allows writing user progress through the instructor process. This takes an `account_id` and `progress` (integer representation of the users progress, 1-5). You can query using `?account_id=[id]` to retrieve progress.

 `/apps/cms/api/salesforce/schools` and `/api/schools` - Returns a list of adoption schools from Salesforce.
 You can also filter on this API by the following fields:
 - `name` [string]
 - `id` [int]
 - `type` [string]
 - `physical_country` [string]
 - `physical_state_province` [string]
 - `physical_city` [string]
 - `key_institutional_partner` [bool]
 - `achieving_the_dream_school` [bool]
 - `testimonial` [bool]



 These are convience endpoints. They redirect to the Wagtail API v2 endpoint (`/apps/cms/api/v2/pages/[id]`)

 `/apps/cms/api/books` - Returns a list of books, with their slug and some information needed to render the subjects page. Wagtail API endpoint: `/api/v2/pages/?slug=subjects`.

 `/apps/cms/api/books/[slug]` - Returns details about a book. Wagtail API endoint: `/api/v2/pages/?slug=[book-slug]`.

 `/apps/cms/api/news` - Returns the content of the news pages and a list of articles. Wagtail API endpoint: `/api/v2/pages/?slug=openstax-news`.

 `/apps/cms/api/news/[slug]` - Returns the content of a news article. Wagtail API endpoint: `/api/v2/pages/?slug=[news-article=slug]`.

 `/apps/cms/api/pages` - Returns a page based on slug, eg. `/api/pages/openstax-homepage`. Wagtail API endpoint: `/api/v2/pages/?slug=openstax-homepage`.
