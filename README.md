# Blast_Cache

This is a system for storing, serving and tracking BLAST and PSI_BLAST PSSM
files.

## Installation

1. yum install postgresql-contrib (for hstore extension)
2. pip -r requirements
3. Add blast_cache db to postgres
4. Enable hstore extension (CREATE EXTENSION hstore)
5. Add blast_cache_user to postgre
6. Run migrations
7. Add manage.py createsuperuser

## API

## Start with
python manage.py runserver --settings=blast_cache.settings.dev
