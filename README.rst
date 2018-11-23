Installation
============

Tachyonic Luxon currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6, 3.7.


CPython
--------

A universal wheel is available on PyPI for Luxon. Installing it is as simple as:

.. code:: bash

    $ pip3 install luxon

Installing the Luxon wheel is a conveniant way to get up and running quickly
in a development environment, but for an extra speed boost when deploying your
application in production, Luxon can compile itself with Cython.

The following commands tell pip to install Cython, and then to invoke Luxon's
setup.py, which will in turn detect the presence of Cython and then compile
the cythonized Luxon framework with the system's default C compiler.

.. code:: bash

	$ pip3 install cython
	$ pip3 install luxon


Source Code
-----------

Luxon infrastructure and code is hosted on `GitHub <https://github.com/TachyonicProject/luxon>`_.
Making the code easy to browse, download, fork, etc. Pull requests are always
welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonicProject/luxon.git

Once you have cloned the repo or downloaded a tarball from GitHub, you
can install Tachyon like this:

.. code:: bash

    $ cd luxon
    $ pip3 install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your development area, and then run the following to install it using
symbolic linking, so that when you change your code, the changes will be
automatically available to your app without having to reinstall the package.

**Keep in mind Cythonized C code for all modules is included during install
or develop. During development code alterations you need run setup.py after
each change.**

.. code:: bash

    $ cd luxon
    $ python3 setup.py develop

During development without explicitly running **setup.py** after each change,
you can use the following. It clears the compiled .cpython.so modules to ensure
code is loaded from Python sources.

.. code:: bash

    $ python3 setup.py clean

You can manually test changes to the luxon by switching to the
directory of the cloned repo:

.. code:: bash

    $ python3 setup.py test
