Installation
============

Tachyonic Luxon currently fully supports `CPython <https://www.python.org/downloads/>`__ 3.6, 3.7.

Dependencies
------------
This version is tested on Linux Ubuntu 18.04 LTS. Pythona >= 3.6.

The general requiremennt is a POSIX Compliant Unix Operating System with all software dependencies.

Some modules are extended using C++ for performance and providing functionality such as POSIX Shared Memory IPC. The Luxon framework requires libboost >= 1.65 and cython.

Ubuntu 
~~~~~~
.. code:: bash

    $ sudo pip3 install cython
    $ sudo apt install libboost-all-dev

MAC OS X
~~~~~~~~
The assumption here is that your using MACPorts.

.. code:: bash

    $ sudo pip3 install cython
    $ sudo port install boost

CPython
--------

A universal wheel is available on PyPI for Luxon. Installing it is as simple as:

.. code:: bash

    $ sudo pip3 install luxon

Source Code
-----------

Luxon infrastructure and code is hosted on `GitHub <https://github.com/TachyonicProject/luxon>`_.
Making the code easy to browse, download, fork, etc. Pull requests are always welcome!

Clone the project like this:

.. code:: bash

    $ git clone https://github.com/TachyonicProject/luxon.git

Once you have cloned the repo or downloaded a tarball from GitHub, you
can install Tachyon like this:

.. code:: bash

    $ cd luxon
    $ sudo pip3 install .

Or, if you want to edit the code, first fork the main repo, clone the fork
to your development area, and then run the following to install it using
symbolic linking, so that when you change your code, the changes will be
automatically available to your app without having to reinstall the package.

.. code:: bash

    $ cd luxon
    $ sudo python3 setup.py develop

You can manually test changes to the luxon by switching to the
directory of the cloned repo:

.. code:: bash

    $ python3 setup.py test
