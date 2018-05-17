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


Tutorial
=========

In this tutorial you will walk through building simple web interface. The same principles with different methods and responder code would be used for REST API.

The first thing we do is install Luxon inside a fresh virtualenv. 

.. code:: bash

    $ mkdir myapp
    $ cd myapp
    $ virtualenv .venv
    $ source .venv/bin/activate
    $ pip install luxon

A project requires its own top-level python package to be called the same as the project. We create a 'myapp' directory inside of the first 'myapp'.

.. code:: bash

    $ mkdir myapp
    $ touch myapp/__init__.py


Next we create a new file for the entry point of the application. This is the wsgi file.

.. code:: bash

    $ touch myapp/wsgi.py

Open wsgi.py in your favourite text editor and add following lines:

.. code:: python

    from luxon.core.handlers.wsgi import Wsgi

    application = Wsgi(__name__)

A WSGI application is just a callable with a well-defined signature so that you can host the application with any web server that understands the WSGI protocol. However we are not going to use that file here.

You need to create a static folder which hosts the applications static content. Such as images, css, javascript and more.

.. code:: bash

    $ mkdir myapp/static
    $ touch myapp/static/empty

You need to create a template folder which hosts the applications Jinja2 Templates.

.. code:: bash

    $ mkdir myapp/templates

To test your application you can run the following command to start up webserver on 127.0.0.1 port 8000. However for this builtin test server to work you need to install gunicorn.

.. code:: bash

	$ pip install gunicorn

Once you have installed it start the application like so.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapp

myapp is the directory within the virtualenv directory. The top level package of the application.

You can now browse to http://127.0.0.1:8000

If you browse to http://127.0.0.1:8000/static you should see the static folder with a file 'empty'

Stop the webserver and lets create a simple responder/resource/view.

.. code:: bash

    $ touch myapp/home.py
    $ touch myapp/templates/home.html

Edit myapp/home.py with your editor and add the following lines.

.. code:: python

    from luxon import register_resource
    from luxon import render_template

    @register_resource('GET', '/')
    def homepage(req, resp):
        resp.content_type = 'text/html; charset=utf-8'
        return render_template('myapp/home.html')

Edit myapp/templates/home.html with your editor and add the following lines.

.. code:: html

    <html>
        <head>
            <title>Homepage</title>
        </head>
        <body>
            <h1>Welcome to Myapp</h1>
        </body>
    </html>

Finally, modify myapp/wsgi.py to import our new app:

.. code:: python

    from luxon.core.handlers.wsgi import Wsgi

    application = Wsgi(__name__)
    from myapp import home

Now start with the webserver again.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapp
	
Browse to http://127.0.0.1:8000. You should see the 'Welcome to Myapp'

Classes
===========

.. toctree::
    :maxdepth: 2
    :titlesonly:

    request
    response
    


