Command Line Tool
==================

Luxon ships with a cli ``luxon`` command, which allows one to initialize application directory structures, databases, and even start a web server.

**Usage**

.. code:: bash

    $ luxon -h
	Luxon Application Framework 0.0.0

	usage: luxon [-h] (-d | -i PKG | -s | -c | -r) [--password PASSWORD] [--ip IP]
		     [--port PORT]
		     path

	Luxon Application Framework 0.0.0

	positional arguments:
	  path                 Application root path

	optional arguments:
	  -h, --help           show this help message and exit
	  -d                   Create/Update Database
	  -i PKG               Install/Update application in path specified
	  -s                   Start Internal Testing Server (requires gunicorn)
	  -c                   Clean Sessions
	  -r                   Generate RSA Private/Public Key pairs
	  --password PASSWORD  RSA Private Key Password
	  --ip IP              Binding IP Address (127.0.0.1)
	  --port PORT          Binding Port (8080)


For example, to set up the required directory structure in /var/www/myapp, and
populate it with the files required for python package *mypackage*, run with the ``-i`` switch such as:

.. code:: bash

    $ cd /var/www
    $ luxon -i mypackage myapp

To start web server on port 8000 for application *myapp*:

.. code:: bash

    $ luxon -s --port 8000 myapp

