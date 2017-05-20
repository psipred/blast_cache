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
1. GET Requests
* blast_cache/list/ : List every single entry in the db
* blast_cache/list/[MD5] : list all unexpired entries in the db with this MD5
* blast_cache/entry/[MD5]?[param...]=[value]... : retrieve unexpired single unique record given MD5 and uniquely specifying params

2. POST Requests
* blast_cache/entry : required fields include

When posting PSSM string data it needs to be esacped properly so that it
does not get read as json on submission (see line 98 of run_blast.py),
.replace('"', '\\"').replace('\n', '\\n'). This also means that these
escape sequences must be removed when data is retrieved

### Required POST parameters

* name: A short easy to remember identifier for the cache entry
* md5:  The md5 hash of the protein sequence for the cache entry
* file_type: An integer reflecting the file type; 1: PSSM, 2: CHK
* blast_hit_count: An integer listing the number of blast hits
* runtime: An integer listing the blast runtime in seconds
* data: A dict containing the file_data (required)

## Test with
python manage.py test --settings=blast_cache.settings.dev

## Start with
python manage.py runserver --settings=blast_cache.settings.dev
