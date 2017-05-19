# Blast_Cache

This is a system for storing, serving and tracking BLAST and PSI_BLAST PSSM
files.

## Installation

1. yum install postgresql-contrib (for hstore extension)
2. pip install -r requirements/bast.txt
3. Add blast_cache db to postgres
4. Enable hstore extension (CREATE EXTENSION hstore)
5. Create test template for the test db
    CREATE DATABASE hstemplate
    \c hstemplate
    CREATE EXTENSION hstore
    update pg_database set datistemplate=true  where datname='hstemplate';
5. Add blast_cache_user to postgres
    CREATE USER blast_cache_user WITH PASSWORD '';
    ALTER USER username CREATEDB;
6. Run migrations
7. Add 'manage.py createsuperuser'

## API
1. GET
* blast_cache/list/ : List every single entry in the db
* blast_cache/list/[MD5] : list all unexpired entries in the db with this MD5
* blast_cache/entry/[MD5]?[param...]=[value]... : retrieve unexpired single unique record given MD5 and uniquely specifying params

2. POST
* blast_cache/entry

## Test with
python manage.py test --settings=blast_cache.settings.dev

## Start with
python manage.py runserver --settings=blast_cache.settings.dev
