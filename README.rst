===========================
defpage.com metadata server
===========================


Create PostgreSQL database
-------------------------

Create user `defpage`, database `defpage` and make him owner::

  # su - postgres
  $ createuser -lsWRD defpage_meta
  (see password in .ini file)
  $ createdb defpage_meta
  $ echo "alter database defpage_meta owner to defpage_meta;" | psql defpage_meta

Deploy
======

Install system dependencies::

  $ sudo apt-get install libpq-dev

Create virtual environment and deploy site within it::

  $ git clone git@spacta.com:defpage_meta.git
  $ cd defpage_meta
  $ virtualenv --no-site-packages --distribute .

Install shared python library for defpage (take it here: git@spacta.com:defpage/pylib.git)::

  $ bin/pip install -e [ path_to_pylib ]

Install site::

  $ bin/pip install -e .

Run tests::

  $ bin/python setup.py test

Run site for development::

  $ bin/pserve development.ini --reload

Upgrading
=========

Apply sql pathces::

  $ psql -U defpage_meta < sql/patch.sql
