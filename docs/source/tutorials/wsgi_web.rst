.. webapp_tut:

================
Web App Tutorial
================

In this tutorial we will walk through building a simple web interface with Luxon. The same principles that were used to build the API will be used, with different methods and responder code. Luxon provides many powerful tools that will make every step of the process more convenient.
If you have not already installed Luxon you will need to do so: :ref:`Installation<install>`

This tutorial follows on the API Tutorial, eventually we will write responders that will communicate with the API. That way we avoid double work. The API that we have already coded will handle the database etc. The Web App will interface between a user and the API so the user will be exposed to the API via rendered HTML rather than direct API calls. This tutorial uses some assumes some dependencies are installed as per the API tutorial.

Similarly to the API tutorial we will start by setting up and deploying a package.

Part 1: Setting up a Python Package
--------------------------------------------------------------

In order to have a fully functioning web application we need to create a python package that we can install as a pip library. Then we will be able to deploy the package as a project from where we will launch the webserver. 

We will create the package in a development directory and then we will deploy the project in an *app* directory. All the source code will live in the development directory and the application will be launched from the *app* directory. We will first create a basic python package and then deploy it as soon as it's done. We will install the package in such a way that we can keep working on the source code and see those changes when we launch the webserver in the project. Then we can build the package piece by piece and test it along the way.

So on to the package, let's call it *myapp*:

Create a working directory where we can develop the package, the actual code will go in an nested directory with the same name :

.. code:: bash
    
	$ mkdir myapp
	$ cd myapp
	$ mkdir myapp

In order to install the package we need a **setup.py** file in the top directory:

.. code:: bash

	$ touch setup.py

Let's keep the content of our **setup.py** as simple as possible:

.. code:: python

	from setuptools import setup

	setup(name = 'myapp',
	      version = '0.01',
	      description = 'Web App Tutorial',
	      packages = ['myapp'])

We also need a **__init__.py** file in the nested directory, we can leave it empty.

.. code:: bash

	$ touch myapp/__init__.py

This is all we need for a simple python package, it is now installable. However before we install it we need to add a few files that Luxon will need. The **settings.ini** file can be left empty.

.. code:: bash
	
	$ touch myapp/settings.ini
	$ touch myapp/policy.json
	$ touch myapp/wsgi.py

Luxon's minimum requirement for a **policy.json** file is an empty JSON object:

.. code:: json

	{}


The **wsgi.py** file is the entry point to our application we can start off by adding these lines to it:

.. code:: python

	from luxon.core.handlers.wsgi import Wsgi

	application = Wsgi(__name__)

    	from myapp import views

		

You can read more about Luxon's Wsgi handler :ref:`Here<wsgi_hand>`

We also need to add a **static** directory which Luxon will copy over to the Project. Later we will use it to house the static content for our server.

.. code:: bash
	
	$ mkdir myapp/static
	$ touch myapp/static/empty

We can now install our package, let's use pip's *-e* switch which will install it with an egg link, this will allow us to edit the source code after the installation. 

.. code:: bash
	
	$ pip3 install -e .

Part 2: Deploying a Python package with Luxon
-------------------------------------------------

Now that we have our package installed as python library and we can deploy it as we would on server.

Let's create a project directory named *app* next to our *myapp* package directory, in the *app* directory we will make another *myapp* directory in which to deploy *myapp*:

.. code:: bash

	$ cd ..
	$ mkdir app
	$ cd app 
	$ mkdir myapp

Everything is now set up for us to deploy our package with Luxon:

.. code:: bash 

	$ luxon -i myapp myapp 

This does a number of things, it copies over the **policy.json**, **settings.ini**, and **wsgi.py** files from the package directory as well as creating **templates** and **tmp** directories inside **myapp**. The **tmp** directory is where all the session data will live. The **templates** directory can house servable *html* templates which can overwrite templates from the package. We won't actually write any code in the project directory, all of that will still happen in the package directory. We will however launch the webserver from the deployment directory, so I suggest keeping a separate terminal open here while we work. 

We can't yet test if our project was successfully deployed however because we still need to create the *views* module which the **wsgi.py** file imports. We will implement that module in the next step. 

We are simultaneously using two directories, the package and the project. We will mostly be working in the package directory to write code but we will be going back to the project directory to start the server. Make sure not to get confused between the two. Before we move on let's clarify what the directory structure looks like at this point:

.. code:: text

	myapp/
	  setup.py
	  myapp/
	    __init__.py
	    setting.ini
	    policy.json
	    wsgi.py
	  static/
	    empty

	app/
	  myapp/
	    tmp/
	    templates/
	    static/
	      empty
	    settings.ini
	    policy.json
	    wsgi.py
	 
We are finally ready to start working on the Web Application! Leave this terminal open to launch the webserver in future and open a new one in the package directory.

Part 3: Homepage View
---------------------------
	 
Now we can start building our Web App by creating a homepage view. The views will exist as their own module in the package. Let's create the module in our package directory at: **myapp/myapp**

.. code:: bash

	mkdir views
	touch views/__init__.py
	
To start off we will create a simple view that will respond to a "GET" request to the homepage "/".

.. code:: bash

	touch views/home.py

We will implement the view as a class in **views/home.py**:

.. code:: python
	
	from luxon import register, render_template ,router
	from luxon.constants import TEXT_HTML

	@register.resources()
	class home():
		# define the route
		def __init__(self):
			router.add(('GET'),'/',self.home)

		# define the view 
		def home(self,req,resp):
			# set response obect content type 
			resp.content_type = TEXT_HTML
			# return a pretty html template 
			return render_template('myapp/home.html')

As you can see the main difference between the Web App homepage view and the API homepage view is that we return an HTML template that will be compiled by a browser and shown to a user, instead of a JSON object. This is made easy by using Luxon's *render_template* module. Of course for this to work we must first write the HTML which our view returns.

Remember to import the view in **views/__init__.py**:

.. code:: python

	import myapp.views.home

Let's make a *templates* directory in our *package* directory to house the HTML templates that we will serve. Note that this will be separate from the *templates* directory in the *app* directory.

.. code:: bash

	$ mkdir templates
	$ touch templates/home.html

The HTML template that the homepage view responds with will go in **templates/home.html**, we'll keep the code simple:

.. code:: html

	<html>
	    <head>
		<title>Homepage</title>
	    </head>
	    <body>
		<h1>Welcome to Myapp</h1>
	    </body>
	</html>
	

Now we can test the view. Launch the webserver from the terminal open in our *app* directory.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapp

When we browse over to http://127.0.0.1:8000 we should see our HTML homepage in all it's glory.













