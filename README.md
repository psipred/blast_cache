# Blast_Cache

This is a system for storing, serving and tracking BLAST and PSI_BLAST PSSM
files.

## Installation

1. yum install postgresql-contrib (for hstore extension)
2. pip -r requirements
3. Add blast_cache db to postgres
4. Enable hstore extension (CREATE EXTENSION hstore)
5. Create test template for the test db
    CREATE DATABASE hstemplate
    \c hstemplate
    CREATE EXTENSION hstore
    update pg_database set datistemplate=true  where datname='hstemplate';
5. Add blast_cache_user to postgre
6. Run migrations
7. Add 'manage.py createsuperuser'

## API


## Test with
python manage.py test --settings=blast_cache.settings.dev

## Start with
python manage.py runserver --settings=blast_cache.settings.dev
