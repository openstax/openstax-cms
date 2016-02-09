Openstax CMS
=======================

Built using [Wagtail CMS](http://wagtail.io).

### Dependencies
* [PostgreSQL](http://www.postgresql.org)
* [PIP](https://github.com/pypa/pip) >=8.0.0

### Installation

With PostgreSQL running (and configured to allow you to connect as the 'postgres' user - if not, you'll need to adjust the `createdb` line and the database settings in openstax/settings/base.py accordingly), run the following commands:

    git clone https://github.com/Connexions/openstax-cms.git
    cd openstax-cms
    pip install -r requirements/dev.txt
    createdb -U postgres openstax
    ./manage.py migrate
    ./manage.py createsuperuser
    ./manage.py runserver

### Testing

Run with ``./manage.py test``

### SQLite support

SQLite is supported as an alternative to PostgreSQL - update the `DATABASES` setting
in openstax/settings/base.py to use `'django.db.backends.sqlite3'` and set `NAME` to be the full path of your database file, as you would with a regular Django project.

### APIs

There are two REST APIs that can be used to access webpage content and other resources such as images.  The first is implemented using [Wagtail's API framework](http://docs.wagtail.io/en/v1.0/reference/contrib/api/index.html), and can be accessed through the links ``/api/v1/pages/``, ``/api/v1/images/``, ``/api/v1/documents/``.  The second is implemented using [Django's REST API framework](http://www.django-rest-framework.org/) and can be accessed through the link ``/api/v0``.
