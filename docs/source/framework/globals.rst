.. _globals:

=======
Globals
=======

It is often needed that 'middleware', 'responders', 'helpers' and perhaps 'utilities' have access to objects within the context of the running application. To provide this context there is the big 'g' global. 

The global allows us to provide convenient errors when working outside of the context of application or request where a responder is not being used.

All requests are placed in threads, even as per WSGI. Hence the request can only be accessed from a utility function for example when a request is being processed.

There are builtin globals such a *'current_request', 'app' and 'router'*.

Context
-------
All middleware and responders __init__ is within the global context of the python namespace. Hence what you do here happens before a request is even made. You can use the constructors to establish database connection for example. Then reference it in 'g'. 

Once a thread is processing a request it has access to globals via 'g' and utilities, helpers can access request data from g.current_request. g.current_request is builtin which only references the request object for the specific thread.

Request objects simply provides a representation of the client request. Such as route, method and payload. Different handlers such as wsgi extend the request methods and properties.

Using 'g' by example
=====================

**The following raises an error**

.. code:: python

    from luxon import g

    print(g.app.app_root) # Will Raise NoContextError. 

**The following works as expected**

.. code:: python

    from luxon import g
    from luxon.core.handlers.wsgi import Wsgi

    app = Wsgi(__name__)

    # G App is equal to app.
    print(g.app.app_root) # Works

Using 'g' for your own purpose
------------------------------
You can create global objects on each process and reference them in 'g'.

.. code:: python

    from luxon import g

    db = connect_to_db()

    g.db = db

Access the request object
==========================

.. code:: python

    from luxon import g

    # However this must be done within the context.
    print(g.current_request.method)

Globals Class
=================

.. autoclass:: luxon.core.globals.Globals
    :members:
	
	.. automethod:: models(self)
        .. automethod:: middleware_pre(self)
        .. automethod:: middleware_resource(self)
        .. automethod:: middleware_post(self)
        .. automethod:: router(self)
    
