Openstax CMS
=======================

Built using [Wagtail CMS](http://wagtail.io).

### Dependencies
* [PostgreSQL](http://www.postgresql.org)
* [PIP](https://github.com/pypa/pip)

### Installation

With PostgreSQL running (and configured to allow you to connect as the 'postgres' user - if not, you'll need to adjust the `createdb` line and the database settings in openstax/settings/base.py accordingly), run the following commands:

    git clone https://github.com/Connexions/openstax-cms.git
    cd openstax-cms
    pip install -r requirements/dev.txt
    createdb -U postgres openstax
    ./manage.py migrate --no-initial-data
    ./manage.py loaddata site.json
    ./manage.py createsuperuser
    ./manage.py runserver

### SQLite support

SQLite is supported as an alternative to PostgreSQL - update the `DATABASES` setting
in openstax/settings/base.py to use `'django.db.backends.sqlite3'` and set `NAME` to be the full path of your database file, as you would with a regular Django project.

### Backing up data for loaddata

This will overwrite the current site data. This is mostly used to pass a workable site around between devs. 
Run:

    ./manage.py dumpdata --natural-foreign --indent=4 -e contenttypes -e auth.Permission -e sessions -e wagtailcore.pagerevision > site.json

_There is currently an issue where the site export table has a duplicate entry and breaks upon import. The best way to fix this is not remove the extra site from this dump. Otherwise, remove it from the database manually. TODO: make this not happen_
