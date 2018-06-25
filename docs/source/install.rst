.. _install:

Installation
============

Luxon Framework currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6.

Installing from PyPi
--------------------
.. code:: bash

    $ pip3 install luxon


Installing from Source Code
---------------------------

Luxon infrastructure and code is hosted on `GitHub <https://github.com/TachyonicProject/luxon>`_.                                   
Making the code easy to browse, download, fork, etc. Pull requests are always welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonicProject/luxon.git

Once you have cloned the repo or downloaded a tarball from GitHub, you 
can install Luxon like this:

.. code:: bash

    $ cd luxon
    $ pip3 install .

Or, if you want to contribute to the code, first fork the main repo, clone the fork
to your desktop, and then run the following to install it with the editable option (-e), so that changes do not require
re-installation:

.. code:: bash

    $ cd luxon
    $ pip3 install -e .

You can manually test changes to the luxon by switching to the 
directory of the cloned repo:

.. code:: bash

    $ pip3 install -r requirements-dev.txt
    $ paver test
