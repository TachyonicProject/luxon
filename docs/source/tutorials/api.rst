API Tutorial
=============

In this tutorial we will build a simple API with the Luxon framework. We will be able to create, read, update and delete users in a database as well as upload and download files with it. Our API will eventually communicate with a Web Aplication that we will also develope with Luxon.
If you have not already installed Luxon you will need to do so: :ref:`Installation<install>`

Through API calls we will be able to:

	- Create, Read, Update and Delete Users
	- Assign Roles to Users
	- Upload and Download Files

Step 1: Starting a Python Package and Firing up a Web Server with Luxon
------------------------------------------------------------------------

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

Now we almost have everything to launch a webserver that can serve dynamic Python content. Except of course the webserver itself. We will use Gunicorn_

.. _Gunicorn: http://gunicorn.org

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
	from views import homepage
	
Now we can start the webserver again with 

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

When we browse over to http://127.0.0.1:8000 we should be met by our Hello message  

Step 3: Completing the Package
-------------------------------

Before we can add/remove users with our API we have to do some more busy work. In order to create a user, our webserver needs a database to store that user in. Setting up a database in our package is a matter of a simple Luxon command, however to do that we need to install the package. We already created the **settings.ini** and **__init__.py** files so the package is almost complete. All we still need to be able to install it is a **setup.py** file in the outer *myapi* directory.

.. code:: bash

	$ touch setup.py

Make sure you have *setuptools* installed:

.. code:: bash

	$ pip install setuptools

We will keep the contents of the file simple, copy in the following: 

.. code:: python

	from setuptools import setup

	setup(name = 'myapi',
	      version = '4.20',
	      description = 'Tutorial API',
	      packages = ['myapi'])

Now we sould be able to install the *myapi* package as a pip module:

.. code:: bash

	$ pip3 install .

Once the package was successfully we can set up the database in the current working directory with Luxon:

.. code:: bash

	$ luxon -d myapi



Step 4: Creating a Model
-------------------------

A model is a useful data structure that Luxon can use to automatically create/update databases. You can read more about models :ref:`Here<models>`.

Before we can can get serious with our API, lets create a user model. We will only create one model, so place it in the same directory as all the other *.py* files.

.. code:: bash

	$ touch myapi/models.py

The model can have any number of members with highly specific fields provided by Luxon. In this case we will keep it simple. We'll give our users a name, age and unique, universally unique identifier that will double as the primary key.

.. code:: python

	from uuid import uuid4
	from luxon import register
	from luxon import SQLModel


	@register.model()
	class User(SQLModel):

	    id = SQLModel.Uuid(default = uuid4)
	    name = SQLModel.Text()
	    age = SQLModel.Integer()
	    primary_key = id


Again we use Luxon's *register* module to register the Model and allow it to be used by our API. We use Luxon's SQLModel to define the class and get the valid fields. Very convenient.

Step 5: Getting serious with the API
---------------------------------------

Now that we have a model we can write more sophisticated views to make use of it. Since we will end up having a number of views to perform different actions with users (Create/Read/Update/Delete) we will group them toghether in a class. This will work slightly differently in that we will use the **register.resources** method to register the view and we will specify all the routes in the constructor. To specify the routes we will use Luxon's **router** module.

Lets add the code to our **views.py** file, remember to import *router* and the model:

.. code:: python

	from luxon import register
	from luxon import router
	from models import User 


	@register.resource('GET','/')
	def homepage(req,resp):
		return "HELLLLOOOOO"

	@register.resources()
	class Users(object):
		def __init__(self):
			# attach user view to /create route with a POST method
			router.add('POST','/create', self.create)

		#view to create user
		def create(self,req,resp):
			# create user object from User model
			user = User()
			# get body of api request from req object
			create = req.json.copy()
			# update User object with request information
			user.update(create)
			# save new user in database
			user.commit()
			# return user object 
			return user
	

We also have to import the new view in our **wsgi.py** file:

.. code:: python

	from luxon.core.handlers.wsgi import Wsgi

	application = Wsgi(__name__)
	from myapi import views
	from views import homepage
	from views import Users

Step 6: Testing the API
-------------------------

Default browsers are great for sending GET requests to our API, but we want to be able to send other kinds of requests too. Let's use Postman_, a useful tool to test APIs. 

.. _Postman: https://www.getpostman.com

Fire up Postman so we can create a user.

Create a POST request with "http://127.0.0.1:8000/create" in the *request URL* bar. Next we write the body of the request which will contain all the information that we will send to create the new user as a JSON object:

.. code:: json

	{
		"name":"Ricky T Dunigan",
		"age": 40
	}

Hit send. We should see a returned JSON object with the information we specified as well as an *id*

.. code:: json

	{
	    "id": "579276f9-b1ae-4455-a503-ec50c46e6c16",
	    "name": "Ricky T Dunigan",
	    "age": 40
	}

Step 7: Fleshing out the API
------------------------------

We have already created the "create" view. The rest of the views are created in a similar way. The *users* view, which returns all the users in the database, is slightly more complicated. It requeres a connection object wich will execute a SQL query. Remember to import *db* from Luxon wich will allow us to easily create a connection objec. The rest of the views are fairly trivial, here is the complete code for **views.py**:

.. code:: python

	from luxon import register , router , db
	from models import User 

	@register.resource('GET','/')
	def homepage(req,resp):
		return "HELLLLOOOOO"

	@register.resources()
	class Users(object):
		def __init__(self):
			# attach user view to /create route with a POST method
			router.add('POST','/create', self.create)
			router.add('GET','/users', self.users)
			router.add('GET','/user/{id}', self.user)
			router.add(['PUT','PATCH'],'/user/{id}', self.update)
			router.add('DELETE','/user/{id}', self.delete)

		#view to create user
		def create(self,req,resp):
			# create user object from User model
			user = User()
			# get body of api request from req object
			create = req.json.copy()
			# update User object with request information
			user.update(create)
			# save new user in database
			user.commit()
			# return user object 
			return user

	
		#view to return all users
		def users(self, req, resp):

			# hardcode sql query
			sql = "SELECT * FROM user"

			# connection to database
			with db() as conn:
				# execute sql command to get a cursor obj
				result = conn.execute(sql)
				# fetch information from cursor obj
				result = result.fetchall()

			return result


		#view to retrun a user
		def user(self,req,resp,id):
			user = User()
			# pass id from url to user object
			user.sql_id(id)
			return user


		#view to update a user
		def update(self,req,resp,id):
			# find user
			user = User()
			user.sql_id(id)

			# fetch update information from request
			create = req.json.copy()

			#update specific user
			user.update(create)
			user.commit()

			return user

		#view to delete a user
		def delete(self,req,resp,id):

			user = User()
			user.sql_id(id)

			# fetch update information from request
			create = req.json.copy()

			#delete specific user
			user.delete()
			user.commit()

			return user


One thing to note is the *id* argument in the views that perform an opperation on a specific user. This argument is taken directly from the url. To test these views, simply copy the *id* string of the specific user and paste it after the route in the url. For example:

.. code:: text

	http://127.0.0.1:8000/user/0633ccbb-2fbf-4768-82a7-bc1ee1eea529

















