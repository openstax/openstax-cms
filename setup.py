# -*- coding: utf-8 -*-
import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='openstax-cms',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    license='BSD License',  # example license
    description='The Openstax CMS',
    long_description=README,
    url='https://www.openstax.org/',
    author='mwharrison, richhart',
    author_email='openstax@rice.edu',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.9',  # replace "X.Y" as appropriate
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',  # example license
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        # Replace these appropriately if you are stuck on Python 2.
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=[
        "beautifulsoup4==4.4.1",
        "Django==1.9.1",
        "django-appconf==1.0.1",
        "django-compressor==2.0",
        "django-libsass==0.6",
        "django-modelcluster==1.1",
        "django-overextends==0.4.1",
        "django-taggit==0.17.6",
        "django-treebeard==3.0",
        "djangorestframework==3.3.2",
        "html5lib==0.9999999",
        "libsass==0.8.2",
        "Pillow==3.1.0",
        "psycopg2==2.6",
        "pytz==2015.7",
        "six==1.10.0",
        "sphinx-me==0.3",
        "Unidecode==0.4.18",
        "wagtail==1.3.1",
        "wheel==0.24.0",
        "Willow==0.2.2"
    ]
    
)