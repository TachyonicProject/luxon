.. _database:

============
Database API
============

Luxon provides a standard PEP-0249 compliant Database interface currently supporting MySQL and SQLite3. 

NOTE:
    Pooling is automatically provided for databases with exception to SQLite3.
    SQLite3 is not threadsafe natively so only locking is provided. Keep in mind
    SQLite3 will be far slower than others due to the locking mechanisem, unless
    no threads are used. Recently SQLite has support for threading but requires
    additional dependencies. 

The goal here is to support args as either list or dict. All param style formats are supported as per PEP-0249.

========== ==========================================================
paramstyle Meaning
========== ==========================================================
qmark      Question mark style, e.g. ...WHERE name=?
numeric    Numeric, positional style, e.g. ...WHERE name=:1
named      Named style, e.g. ...WHERE name=:name
format     ANSI C printf format codes, e.g. ...WHERE name=%s
pyformat   Python extended format codes, e.g. ...WHERE name=%(name)s
========== ==========================================================

WARNING:
    You need to ensure you provide the correct args object for the format used.
    e.g. qmark cannot be used when providing a dict.
    This is because qmark has no reference to the dict key.

During iteration or fetch methods all return lists of rows containing dict. The dict keys are equeal to the column names used in the database.

Configuration should be done via *settings.ini*

settings.ini
------------

.. code:: ini

    [database]
    # Type is either 'sqlite3' or 'mysql'
    type=sqlite3

    # Relevent to both MySQL and SQLite3
    database=tachyonic

    # Relevant to only MYSQL
    host=127.0.0.1
    username=dbuser
    password=dbpass

Example Usage
-------------

.. code:: python

    from luxon import db

    with db() as conn:
        res = conn.execute("SELECT.....", [args])
        for row in res:
            print(res['column'])

        # or alternatively:
        with db.cursor() as crsr:
            crsr.execute('.....')
            res = crsr.fetchall()



Code
===============

.. toctree::
    :maxdepth: 2


    connection
    cursor
    except
    args
    drivers
    db





