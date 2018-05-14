=================
Main Entrypoint
=================

When Luxon is installed with pip3, the **luxon** command line executable is generated.
Luxon can used to install other Tachyonic packages for example:

.. code:: bash

	$ luxon -i infinitystone infinitystone

When this **luxon** command is run, with arguments, a script is called which runs the *main.py* file in Luxon. 

The main function interpretes the arguments given in the command line and performs some action on a given package.

The main function provides for several switches to be used, they specify the action to be taken. In the example the **-i** switch was used.



Main Functions
===============

.. _setup:

Setup 
------

.. autofunction:: luxon.main.setup

RSA
----

.. autofunction:: luxon.main.rsa

.. _server:

Server 
---------

.. autofunction:: luxon.main.server

.. _db_crud:

Database CRUD 
----------------

.. autofunction:: luxon.main.db_crud



