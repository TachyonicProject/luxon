API Tutorial
=============

In this tutorial we will build a simple API with the Luxon framework, we will be able to use it to upload and download files. Our API will eventually communicate with a Web Aplication that we will also develope with Luxon.
If you have not already installed Luxon you will need to do so: :ref:`Installation<install>`

Through API calls we will be able to:

	- Create, Read, Update and Delete Users
	- Assign Roles to Users
	- Upload and Download Files

Step 1: Creating a Package and Firing up a Web Server with Luxon
--------------------------------------------------------------------

Let's call the working directory for this project **myapi**.


.. code:: bash

    $ mkdir myapi

A python project requires it's own top-level Python package, with the same name as the project as well as a **__init__.py** file and a **settings.ini** file.

.. code:: bash
    
    $ cd myapi
    $ mkdir myapi
    $ touch myapi/__init__.py
    $ touch myapi/settings.ini

A WSGI file will serve as the entry point to the application. 

.. code:: bash

    $ touch myapi/wsgi.py


We will need to import Luxon's WSGI handler and instanciate a WSGI interface. To achieve this, add the following two lines to the **wsgi.py** file:

.. code:: python

    from luxon.core.handlers.wsgi import Wsgi

    application = Wsgi(__name__)

Now we almost have everything to launch a webserver that can serve dynamic Python content. Except of course the webserver itself. We will use gunicorn

.. code:: bash

    $ pip3 install gunicorn 

We can now finally use Luxon to start the webserver on our local host, with port *8000*

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

Browse over to http://127.0.0.1:8000 to test our new webserver  

We have not provided any static content to serve or any API resources yet.
You should be greeted with an "error not found" message in the form of a JSON object.

.. code:: json 

	{
	    "error": {
		"title": "Not Found",
		"description": "Route not found Method 'GET' Route '/'"
	    }
	}

Step 2: Creating a view with Luxon
------------------------------------
	 
Now we can start building our API by creating views/resources.

.. code:: bash
	
	$ touch myapi/views.py

Let's start by creating a simple view on the homepage that just returns a string

Add the following to **views.py**

.. code:: python

	
	from luxon import register

	@register.resource('GET','/')
	def homepage(req,resp):
		return "HELLLLOOOOO"

To create the view we defined a function that returns the resource we need. Then we decorate the function with Luxon's powerful *register* module which attaches the function to a specific call method, *GET* in this case, and a root "/" in this case. There is also a *register.resources* using a class to impliment a view. 

Finally we need to import our views in the entry point file **wsgi.py**

.. code:: python

	
	from luxon.core.handlers.wsgi import Wsgi

	application = Wsgi(__name__)
	from myapi import views
	
Now we can start the webserver again with 

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

When we browse over to http://127.0.0.1:8000 we should be met by our Hello message  





















