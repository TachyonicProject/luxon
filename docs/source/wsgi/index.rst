====================
WSGI Handler
====================

The WSGI handler provides environment that is fast, flexible, scalable and simple for building 'Web Applications' and APIs. The WSGI handler has minimal dependencies and unncessary abstraction. Templating for example is not initilized if not needed. However once used its pre-initilized for any other requests.

**Hello world in** *'6'* **lines**

.. code:: python

    from luxon.core.handlers.wsgi import Wsgi
    from luxon import register_resource

    application = Wsgi(__name__)

    @register_resource('GET', '/hello')
    def hello(req, resp):
        return 'hello world'



.. toctree::
   :maxdepth: 2

   tutorial
   request
   response
   help
