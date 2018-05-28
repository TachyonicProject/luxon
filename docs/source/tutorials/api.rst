.. api_tut:

API Tutorial
==============

In this tutorial we will build a simple API with the Luxon framework. We will slowly add functionality including authentication an policies and eventually our API will be able to  communicate with a Web Aplication that we will also develop with Luxon.
If you have not already installed Luxon you will need to do so: :ref:`Installation<install>`

Through API calls we will be able to:

	- Create, Read, Update and Delete Users
	- Assign Roles to Users
	- Upload and Download Files

Let's get started with the basics.

Part 1: Setting up a Python Package
--------------------------------------------------------------

In order to have a fully functioning project with a webserver and a database we need to create a python package that we can install as a pip library. Then we will be able to deploy the package as a project, set up the database and launch the webserver. Luxon makes this process very conveneniet. 
We will create the package in a development directory and then we will deploy the project in an *app* directory. All the source code will live in the development directory and the application will be launched from the *app* directory. We will first create a basic python package and then deploy it as soon as it's done. We will install the package in such a way that we can keep working on the source code and see those changes when we launch the webserver in the project. Then we can build the package piece by piece and test it along the way.

So on to the package, let's call it *myapi*:

Create a working directory where we can develop the package, the actual code will go in an nested directory with the same name :

.. code:: bash
    
	$ mkdir myapi
	$ cd myapi
	$ mkdir myapi

In order to install the package we need a **setup.py** file in the top directory:

.. code:: bash

	$ touch setup.py

Let's keep the content of our **setup.py** as simple as possible:

.. code:: python

	from setuptools import setup

	setup(name = 'myapi',
	      version = '0.01',
	      description = 'Tutorial API',
	      packages = ['myapi'])

Make sure that you have *setuptools* installed:

.. code:: bash

	$ pip3 install setuptools

We also need a **__init__.py** file in the nested directory, we can leave it empty.

.. code:: bash

	$ touch myapi/__init__.py

This is all we need for a simple python package, it is now installable. However before we install it we need to add a few files that Luxon will need later on, they will be explained as they become relevant. 

.. code:: bash
	
	$ touch myapi/settings.ini
	$ touch myapi/policy.json
	$ touch myapi/wsgi.py

The **wsgi.py** file is the entry point to our application we can start off by adding these lines to it:

.. code:: python

	from luxon.core.handlers.wsgi import Wsgi

	application = Wsgi(__name__)	

	from myapi import views

You can read more about Luxon's Wsgi handler :ref:`Here<wsgi_hand>`

The **from myapi import views** line imports a module that does not yet exist, this will cause an error if we try to start the a webserver after we have installed our package. Fear not, we will write the module which is imported here in the next step. The reason we put that line in now already is because when we deploy our package with Luxon, Luxon will copy the **wsgi.py** file from the package into the project and we don't want to edit any of the project code after deployment, only the package code. So we make sure the package has everything that we will eventually need. 

Now we can finally isntall our package! We will use pip's *-e* switch which will install it with a sym link, this will allow us to edit the source code after the installation. 

.. code:: bash
	
	$ pip3 install -e .

Part 2: Deploying a python package with Luxon
-------------------------------------------------

Now that we have our package installed as python library and we can deploy it as we would on server.

Let's create a project directory named *app* next to our *myapi* package directory, in the *app* directory we will make another *myapi* directory in which to deploy *myapi*:

.. code:: bash

	$ cd ..
	$ mkdir app
	$ cd app 
	$ mkdir myapi

Everything is now set up for us to deploy our package with Luxon:

.. code:: bash 

	$ luxon -i myapi myapi 

This does a number of things, it copies over the **policy.json**, **settings.ini**, and **wsgi.py** files from the package directory as well as creating **templates** and **tmp** directories inside **myapi**. The **tmp** directory is where all the session data will live, we will get to that later. The **templates** directory is where servable *html* templates will live when we make a Web App, we will get to that in the next tutorial. We won't actully write any code in the project directory, all of that will still happen in the package directory. We will however launch the webserver from the deployment directory, so I suggest keeping a separate terminal open here while we work. 

We almost have everything we need to launch a webserver that can serve dynamic Python content. Except of course the webserver itself. We will use Gunicorn_

.. _Gunicorn: http://gunicorn.org

.. code:: bash

    $ pip3 install gunicorn 

We can't yet test if our project was successufly deployed however because we still need to create the *views* module which the **wsgi.py** file imports. Just hang on, by the end of the next step we will be able to launch a webserver that responds to a call on the homepage. 

We are finally ready to start working on the API! Leave this terminal open to launch the webserver in future and open a new one in the package directory.

Part 3: Creating a view with Luxon
------------------------------------
	 
Now we can start building our API by creating views/resources. The views will exist as their own module in the package. The views module will consume and respond to every call made to our API. The views will import all the code they need from the rest of *myapi* as they need them. Let's create the module in our package directory at: **myapi/myapi**

.. code:: bash

	mkdir views
	touch views/__init__.py
	
To start off we will create a simple view that will respond to a "GET" request to the homepage "/".

.. code:: bash

	touch views/homepage.py

The code to impliment the homepage view:

.. code:: python
	
	from luxon import register

	@register.resource('GET','/')
	def homepage(req,resp):
		return "HELLLLOOOOO"

To create the view we defined a function that returns the resource we need. Then we decorated the function with Luxon's powerful *register* module which attaches the function to a specific request method, *GET* in this case, and a root "/" in this case. There is also a *register.resources* which we will use later to implement views in a class.

For this view to be usable we need also need to import it in the **views/__init__.py** file:

.. code:: python

	import myapi.views.homepage

We can now finally use Luxon to start the webserver on our local host, with port *8000*. Remember that we want to execute this command in the terminal open in our *app* directory.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

When we browse over to http://127.0.0.1:8000 we should be met by our Hello message  

Part 4: Creating a Model
-------------------------

A model is a useful data structure that Luxon can use to automatically create/update databases. You can read more about models :ref:`Here<models>`.

The models we create will live in their own module, same as the views. In this module we will create a **user.py** file to house our *user* model.

.. code:: bash

	mkdir models
	touch models/__init__.py
	touch models/user.py


The model can have any number of members with highly specific fields provided by Luxon. In this case we will keep it simple. We'll give our users a name, age and a universally unique identifier that will double as the primary key. Let's implement it in our **user.py** file:

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

Remember to import our new user model in **models/__init__.py**:

.. code:: python

	from myapi.models.user import User


At this point we need to set up the database in our project so that our API can make use of models. Luckily Luxon has us covered. Go back to the *app* directory and run:

.. code:: bash

	$ luxon -d myapi

You will notice that this has created a **sqlite3** file.

Part5: Getting serious with the API
---------------------------------------

Now that we have a model we can write more sophisticated views to make use of it. Since we will end up having a number of views to perform different actions with users (Create/Read/Update/Delete) we will group them toghether in a class. This will work slightly differently in that we will use the **register.resources** method to register the view and we will specify all the routes in the constructor. To specify the routes we will use Luxon's **router** module.

We need to create another file in our package directory under **views** to house the *users* views:

.. code:: bash

	$ touch views/users 

And remember to import the new view in **views/__init__.py**:

.. code:: python

	import myapi.views.homepage
	import myapi.views.users


Let's impliment the first user view in a class called **Users** in our **views/users.py** file:

.. code:: python
	
	from luxon import register
	from luxon import router
	from myapi.models.user import User

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

Now we can finally test our API. Launch the server again in the *app* directory with:

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

Part 6: Testing the API
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

Part 7: Fleshing out the API
------------------------------

We have already created the "create" view. The rest of the views are created in a similar way. The *users* view, which returns all the users in the database, is slightly more complicated. It requeres a connection object wich will execute a SQL query. Remember to import *db* from Luxon wich will allow us to easily create a connection object. The rest of the views are fairly trivial, here is the complete code for **views/users.py**, note the new imports:

.. code:: python

	from luxon import register , router , db
	from myapi.models.user import User 

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


















