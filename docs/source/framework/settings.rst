.. _settings:

======
Config
======

Luxon performs configuration by using a global *settings* file. The *settings* file can be used globaly and and localy on a per module basis.

Settings
=========

Luxon will attempt to discover the route path when starting the handler e.g. Wsgi.
You can place a *settings.ini* file in the same directory of your wsgi file which is loaded by Wsgi handler. The *settings.ini* file will be read by Luxon's config parser.

settings.ini layout
-------------------

.. code:: ini

    # Main Application configuration
    [application]

    # Global Application name. Its seen in the logs output.
    name = Application

    # Log Level for Application root logger.
    # Default is WARNING
    log_level = WARNING

    # Log to sys.stdout. for root logger.
    log_stdout = True

    # Log to syslog server for root logger.
    # If not defined will not log to server.
    log_server = 192.168.0.1

    # Log Port for syslog server.
    log_server_port = 514

    # Log to file for root logger.
    # If not defined will not log file.
    log_file = /tmp/app.log

    # Per Module configuration.
    [package.module]

    # Log level for specific module.
    log_level = DEBUG

    # Log Stdout for specific module.
    log_stdout = False

    # Log Server for specific module.
    # If not defined will not log to server.
    log_server = 192.168.0.1

    # Log Port for syslog server.
    log_server_port = 514

    # Log to file for module.
    # If not defined will not log file.
    log_file = /tmp/package_module.log


Default settings.ini
---------------------

.. literalinclude:: /../../luxon/core/config/defaults.py
   :lines: 30-68

Configparser
=============

The Python configparser implements a basic configuration language which provides a structure similar to what’s found in Microsoft Windows INI files. You can use this to write Python programs which can be customized by end users easily.

The configuration can be access globally from **g.app.config** which Luxon's Python configparser that has been enhanced by adding more methods to the exisiting base Python configparser.

Config Class
------------
.. autoclass:: luxon.core.config.Config
    :members:

