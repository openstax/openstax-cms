[![Dependency Status](https://gemnasium.com/badges/github.com/openstax/openstax-cms.svg)](https://gemnasium.com/github.com/openstax/openstax-cms)

OpenStax CMS
=======================

Built using [Wagtail CMS](http://wagtail.io).

### Dependencies
* [PostgreSQL](http://www.postgresql.org)
* [Python](https://www.python.org/) >= 3.4
* [PIP](https://github.com/pypa/pip) >=8.0.0

### Installation

Verify you have Python >= 3.4 installed with `python --version` or `python3 --version`.
If not, you can install Python 3 by running `brew install python3`. If you don't have brew installed, see [Homebrew](http://brew.sh/).


With PostgreSQL running (and configured to allow you to connect as the 'postgres' user - if not, you'll need to adjust the `createdb` line and the database settings in openstax/settings/base.py accordingly), run the following commands:

    git clone https://github.com/Connexions/openstax-cms.git
    cd openstax-cms
    pip3 install -r requirements/dev.txt
    createdb -U postgres openstax
    python3 manage.py migrate
    python3 manage.py createsuperuser
    python3 manage.py runserver

### Testing

Run with ``python3 manage.py test --liveserver=localhost:8001 --settings=openstax.settings.dev``

### SQLite support

SQLite is supported as an alternative to PostgreSQL - update the `DATABASES` setting
in openstax/settings/base.py to use `'django.db.backends.sqlite3'` and set `NAME` to be the full path of your database file, as you would with a regular Django project.

### API Endpoints
`/api/v2` - Wagtails API. This serves things like pages, images, and documents - except when it doesn't, see below for exceptions.

`/api/v2/pages` (mostly used with `/api/v2/pages/?slug=[slug]`) returns the `detail_url` for the page content.
 
 `/api/snippets/roles` - Returns list of available roles for a user. This lives in the `snippets` directory.
 
 `/api/sticky` - Returns the text for the sticky note. Lives in the `/api/` directory.
 
 `/api/footer` - Returns the text for the footer. Lives in the `/api` directory.
 
 `/api/errata/[id]` - Returns details for a piece of Errata
 
 `/api/books` - Returns a list of books, with their slug and some information needed to render the subjects page
 
 `/api/mail/send_mail` - Takes post parameters and sends mail through Amazon SES. We prevent spamming by only having a limited set of subjects that it will accept and go to a particular email address. 
 
 `/api/documents` - Custom API endpoint to return all documents with their cloudfront url, this lives in the `api` directory
 
 `/api/images` - Custom API endpoint to return all images with their cloudfront url, this lives in the `api` directory.
 
 `/api/user` - Returns information from accounts, cms, and salesforce about the user. This lives in the `api` directory.
 
 `/api/news` - [Deprecated] - Returns the content of the news pages and a list of articles. This is being deprecated and you should now use `/api/v2/pages/?slug=openstax-news`.
 
 `/api/pages` - [Deprecated] - Returns a page based on slug, eg. `/api/pages/openstax-homepage`. This is being deprecated and you should now use `/api/v2/pages/?slug=openstax-homepage`.
