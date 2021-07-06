# Blast_Cache
This is a system for storing, serving and tracking BLAST and PSI_BLAST PSSM
files.

## Installation

1. yum install postgresql-contrib (for hstore extension)
2. pip install -r requirements/base.txt
3. create logs dir
   mkdir logs
4. Add blast_cache db to postgres
   Add secrets files
   touch base_secrets.json
   touch dev_secrets.json

   Add to base_secrets.json
   {}
   Add to dev secrets.json
   {
     "USER": "blast_cache_user",
     "PASSWORD": "thisisthedevelopmentpassword",
     "SECRET_KEY": "SOMELONG STRING"
   }

## Install the postgres database and then start postgres

   Export the path to wherever postgres has been installed.
   For mac using homebrew this will be in /usr/local/Cellar
   This should look something like:

   ```export PATH="/usr/local/Cellar/postgresql@9.6/9.6.20/bin/:$PATH"```

   ## start postgresql

   ```pg_ctl -D /usr/local/var/postgresql@9.6 -l /usr/local/var/postgresql@9.6/server.log start```

   ## login to the database and create a new database/user
   ```psql -h localhost -d postgres
   ```

This will start the database server on your localhost. You can then go ahead and make a database with associated user.

5.log in to postgres and create:
  CREATE ROLE blast_cache_user WITH LOGIN PASSWORD 'thisisthedevelopmentpassword';
  CREATE DATABASE blast_cache;
  GRANT ALL PRIVILEGES ON DATABASE blast_cache TO blast_cache_user;
  ALTER USER blast_cache_user CREATEDB;
6. still in postgres Enable hstore extension
    CREATE EXTENSION hstore;
7. Create test template for the test db
    CREATE DATABASE hstemplate;
    \c hstemplate
    CREATE EXTENSION hstore;
    update pg_database set datistemplate=true  where datname='hstemplate';
    \c blast_cache
    CREATE EXTENSION hstore;
8. Run migrations
9. from within blast_cache you can now make the migrations and add a superuser

```
python manage.py makemigrations --settings=analytics_automated_project.settings.dev
python manage.py migrate --settings=analytics_automated_project.settings.dev
python manage.py createsuperuser --settings=analytics_automated_project.settings.dev
```

## API
1. GET Requests
* blast_cache/list/ : List every single entry in the db
* blast_cache/list/[MD5] : list all unexpired entries in the db with this MD5
* blast_cache/entry/[MD5]?[param...]=[value]... : retrieve unexpired single unique record given MD5 and uniquely specifying params
* blast_cache/entry/[MD5]?[param...]=[value]&block=true... : retrieve unexpired single unique record given MD5 and uniquely specifying params and if not present create a record and set it to blocked


2. POST Requests
* blast_cache/entry : required fields include

When posting PSSM string data it needs to be escaped properly so that it
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

# Search Scripts

The `scripts/` directory contains scripts that consume this cache API.

### HHBlits Script notes

HHBlits run time is profile length dependent. In degenerate cases this can cause HHBlits to appears to hang for what appears to be an indefinite period. The function `set_hh_evalue()` adjusts the e-value HHBlits uses to recruit sequences based on sequence length. Sequence bins were guestimated using a rough benchmark to sequence runtimes in 2018. Evalues were guessed as reasonable adjustments of factors of 10, without pushing the e-value too low. This means profile differences between server and standalone version of our tools are length dependent. This has impacts on the accuracy of some tools, noteably DISOPRED.
