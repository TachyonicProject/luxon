.. _logger:

Logger
======

Luxon has a built in logger to provide a conveniant high-level common interface with extended functionality.

The logger wraps around python logging facilities and ensures that formatting and handlers are managed within the context of the python interpreter.

The logger can be configured with the *settings.ini* file.

Example Usage
-------------

.. code:: python

    from luxon import GetLogger

    # As per per 282 use the module name.
    log = GetLogger(__name__)

    log.critical('Critical message')
    log.error('Error message')
    log.warning('Warning message')
    log.info('Informational message')
    log.debug('Debug message')

    # Returns bool if in debug mode.
    log.debug_mode() 

GetLogger Class
---------------

.. autoclass:: luxon.core.logger.GetLogger
    :members:

Request Context
---------------

You can append values to each log entry made within the context of a request by using the log dictionary provided by the request.

**An example would be:**

.. code:: python

    req.log['username'] = 'Foo'
    # This would append '(username:Foo) to logs.

