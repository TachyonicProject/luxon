.. _api_tut:

==============
API Tutorial
==============

In this tutorial we will build a simple REST API with the Luxon framework. We will start small and slowly add functionality including authentication. Luxon provides many powerful tools that will make every step of the process more convenient.
If you have not already installed Luxon you will need to do so. (Installation instructions :ref:`here<install>`)
	
Through API calls we will be able to:

	- Create, Read, Update and Delete Users
	- Assign Roles to Users
	

Let's get started with the basics.

Part 1: Setting up a Python Package
--------------------------------------------------------------

In order to have a fully functioning project with a webserver and a database we need to create a python package that we can install as a pip library. Then we will be able to deploy the package as a project, set up the database and launch the webserver. Luxon makes this process very convenient. 

We will create the package in a *development* directory and then we will deploy the project in an *app* directory. All the source code will live in the development directory and the application will be launched from the *app* directory. We will first create a basic python package and then deploy it as soon as it's done. We will install the package in such a way that we can keep working on the source code and see those changes when we launch the webserver in the project. Then we can build the package piece by piece and test it along the way.

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

This is all we need for a simple python package, it is now installable. However before we install it we need to add a few files that Luxon will need. The **settings.ini** file can be left empty. 

.. code:: bash
	
	$ touch myapi/settings.ini
	$ touch myapi/policy.json
	$ touch myapi/wsgi.py

The **policy.json** file is involved with Role Based Access Control, we will get to it much later, for now just put this in it:

.. code:: json

	{
		"role:admin": "'admin' in req.credentials.roles",
		"role:user": "'user' in req.credentials.roles",
		"admin_view": "$role:admin",
		"user_view": "$role:admin or $role:user"
	}

The **wsgi.py** file is the entry point to our application we can start off by adding these lines to it:

.. code:: python

	from luxon.core.handlers.wsgi import Wsgi

	application = Wsgi(__name__)	

	from myapi import views

You can read more about Luxon's Wsgi handler :ref:`Here<wsgi_hand>`

The ``from myapi import views`` line imports a module that does not yet exist, this will cause an error if we try to start the a webserver after we have installed our package. Fear not, we will write the module which is imported here in the next step. The reason we put that line in now already is because when we deploy our package with Luxon, Luxon will copy the **wsgi.py** file from the `package` dir into the `project` dir and we don't want to edit any of the project code after deployment, only the package code. So we make sure the package has everything that we will eventually need.

Now we can finally install our package! We will use pip's *-e* switch which will install it with an egg link, this will allow us to edit the source code after the installation. 

.. code:: bash
	
	$ pip3 install -e .

Part 2: Deploying a Python package with Luxon
-------------------------------------------------

Now that we have our package installed as python library and we can deploy it as we would on a server.

Let's create a project directory named *app* next to our *myapi* package directory, in the *app* directory we will make another *myapi* directory in which to deploy *myapi*:

.. code:: bash

	$ cd ..
	$ mkdir app
	$ cd app 
	$ mkdir myapi

Everything is now set up for us to deploy our package with Luxon:

.. code:: bash 

	$ luxon -i myapi myapi 

This does a number of things, it copies over the **policy.json**, **settings.ini**, and **wsgi.py** files from the
package directory as well as creating **templates** and **tmp** directories inside **myapi**. The **tmp** directory
is where all the session data will live. The **templates** directory is where servable *html* templates will live.
Neither of these directories will be relevant in this tutorial. We won't actually write any code in the project
directory, all of that will still happen in the package directory. We will however launch the webserver from the
deployment directory.

We almost have everything we need to launch a webserver that can serve dynamic Python content. Except of course
the webserver itself. We will use Gunicorn_.

.. _Gunicorn: http://gunicorn.org

.. code:: bash

    $ pip3 install gunicorn 

We can't yet test if our project was successfully deployed however because we still need to create the *views* module
which the **wsgi.py** file imports. Just hang on, by the end of the next step we will be able to launch a webserver that
responds to a call on the homepage.

We are simultaneously using two directories, the `package` and the `project`. We will mostly be working in the `package`
directory to write code but we will be going back to the project directory to start the server, set up the database etc.
Make sure not to get confused between the two. Before we move on let's clarify what the directory structure looks like
at this point:

.. code:: text

	myapi/
	  setup.py
	  myapi/
	    __init__.py
	    setting.ini
	    policy.json
	    wsgi.py

	app/
	  myapi/
	    tmp/
	    templates/
	    settings.ini
	    policy.json
	    wsgi.py
	 
We are finally ready to start working on the API! Leave this terminal open to launch the webserver in future and open a
new one in the package directory.

Part 3: Creating a view with Luxon
------------------------------------
	 
Now we can start building our API by creating views/resources. The views will exist as their own module in the package.
The views module will consume and respond to every call made to our API. The views will import all the code they need
from the rest of the *myapi* modules as needed. Let's create the module in our package directory at: **myapi/myapi**

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
		return "HELLO WORLD!"

To create the view we defined a function that returns the resource we need. Then we decorated the function with Luxon's
powerful *register* module which attaches the function to a specific request method, *GET* in this case, and a Location,
root "/" in this case. The ``req`` and ``resp`` arguments for this function is luxon's WSGI :ref:`Request<wsgi_request>` and
:ref:`Response<wsgi_response>` objects, respectively.

For this view to be usable we need also need to import it in the **views/__init__.py** file:

.. code:: python

	import myapi.views.homepage

We can now finally use Luxon to start the webserver on our local host, with port *8000*. Remember that we want to
execute this command in the terminal open in our *app* directory.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8000 myapi

When we browse over to http://127.0.0.1:8000 we should be met by our Hello message  

Part 4: Creating a Model
-------------------------

A model is a useful data structure that Luxon can use to automatically create/update databases. You can read more about
models :ref:`here<models>`.

The models we create will live in their own module, same as the views. In this module we will create a **user.py** file
to house our *user* model. Let's create the module in our package directory at: **myapi/myapi**

.. code:: bash

	mkdir models
	touch models/__init__.py
	touch models/user.py


The model can have any number of members with highly specific fields provided by Luxon (full list
:ref:`here <model_fields>`). In this case we will keep it simple. We'll give our users a username, password, role and a
universally unique identifier that will double as the primary key. Let's implement it in our **user.py** file:

.. code:: python

	from uuid import uuid4
	from luxon import register
	from luxon import SQLModel


	@register.model()
	class User(SQLModel):

	    id = SQLModel.Uuid(default = uuid4)
	    username = SQLModel.Text()
	    password = SQLModel.Text()
	    role = SQLModel.Enum('user', 'admin')
	    primary_key = id


Again we use Luxon's *register* module to register the Model and allow it to be used by our API. We use Luxon's
SQLModel to define the class and get the valid fields. Very convenient.

Remember to import our new user model in **models/__init__.py**:

.. code:: python

	from myapi.models.user import User


At this point we need to set up the database in our project so that our API can make use of models.
Luckily Luxon has us covered. Go back to the *app* directory and run:

.. code:: bash

	$ luxon -d myapi

You will notice that this has created a **sqlite3** file in the *app/myapp* directory.
Sqlite3 is the default, but luxon also supports MariaDB
MysSQL (see example settings.ini file :ref:`here <mysql_settings>`).

Part 5: Getting serious with the API
---------------------------------------

Now that we have a model we can write more sophisticated views to make use of it. Since we will end up having a number
of views to perform different actions with users (Create/Read/Update/Delete) we will group them together in a class.
This will work slightly differently in that we will use the **register.resources** method to register the views and we
will specify all the routes in the constructor. To specify the routes we will use Luxon's **router** module.

We need to create another file in our package directory under **views** to house the *users* views in the *myapi/myapi*
directory:

.. code:: bash

	$ touch views/users.py

And remember to import the new view in **views/__init__.py**:

.. code:: python

	import myapi.views.homepage
	import myapi.views.users


Let's impliment the first user view in a class called **Users** in our **views/users.py** file:

.. code:: python
	
    from luxon import register, router
    from myapi.models.user import User
    from luxon.utils.password import hash


    @register.resources()
    class Users(object):

        def __init__(self):
            # Assign POST requests to the '/create' path to the create() method
            router.add('POST','/create', self.create)

        #view to create user
        def create(self,req,resp):

            # create user object from User model
            user = User()

            # get body of api request from req object
            create = req.json.copy()

            # hash the password
            if 'password' in create:
                create['password'] = hash(create['password'])

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

Default browsers are great for sending GET requests to our API, but we want to be able to send other kinds of requests
too. Let's use Postman_, a useful tool to test APIs.

.. _Postman: https://www.getpostman.com

Fire up Postman so we can create a user.

Create a POST request with "http://127.0.0.1:8000/create" in the *request URL* bar. Next we write the body of the
request as raw JSON. It contains all the information that we will send to create the new user:

.. code:: json

	{
		"username":"Ricky T Dunigan",
		"password":"hypnotizeminds",
		"role":"admin"
	}

Hit send. We should see a returned JSON object with the information we specified as well as an *id*

.. code:: json

	{
	    "role": "admin",
	    "id": "0e1462d5-f20d-4d69-8546-df549c127f90",
	    "password": "$2b$12$JCWLhldHGWfRmL9z/Nd14OlxTbma3T8hbRFa0ioQWJs49I.5msJX6",
	    "username": "Ricky T Dunigan"
	}

Note that the password has been hashed. We hash the clear text password we receive from the user before we send it to
the database so that even if someone examines the user table in the database all they will see is a useless hash,
the actual password will be safe. More about password hashing in the authentication part of the tutorial.

Part 7: Fleshing out the API
----------------------------

We have already created the "create" view. The rest of the views are created in a similar way.
The */users* path, which returns a view of all the users in the database, is slightly more complicated.
It requires a connection object which will execute a SQL query. Remember to import *db* from Luxon which will allow us
to easily create a connection object. The rest of the views are fairly straight forward, here is the complete code for
**views/users.py**. Note the new imports:

.. code:: python

    from luxon import register, router, db
    from myapi.models.user import User
    from luxon.utils.password import hash

    @register.resources()
    class Users(object):

        def __init__(self):
            router.add('POST','/create', self.create)
            router.add('GET','/users', self.list)
            router.add('GET','/user/{id}', self.user)
            router.add(['PUT','PATCH'],'/user/{id}', self.update)
            router.add('DELETE','/user/{id}', self.delete)

        #view to create user
        def create(self,req,resp):
            # create user object from User model
            user = User()
            # get body of api request from req object
            create = req.json.copy()
            # hash the password
            if 'password' in create:
                create['password'] = hash(create['password'])
            # update User object with request information
            user.update(create)
            # save new user in database
            user.commit()
            # return user object
            return user


        #view to return all users
        def list(self, req, resp):
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
        def user(self, req, resp, id):
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
            # hash the password
            if 'password' in create:
                create['password'] = hash(create['password'])
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




One thing to note is the *id* argument in the views that perform an operation on a specific user. This argument is taken directly from the url. To test these views, simply copy the *id* string of the specific user and paste it after the route in the url. For example:

.. code:: text

	http://127.0.0.1:8000/user/0633ccbb-2fbf-4768-82a7-bc1ee1eea529


Part 8: Authentication with a Login view
-------------------------------------------

Now that we have a simple API up we can start implementing some kind of authentication. Every User has a *username* and *password* which are specified upon creation. Let's create a *login* view that will receive a *username/password* and validate it against the users in the database. Upon validation the view will return a *token* which can then be sent with future API calls to verify the authenticity of the user sending the calls.

Before we do anything else we have to generate RSA keys for our project, Luxon needs them for authentication. We can use Luxon to generate them in our *app* directory:

.. code:: bash 

	$ luxon -r myapi

Now lets create another file in our package directory under **views** to house the *login* views:

.. code:: bash

	$ touch views/login.py

Remember to import the new view in **views/__init__.py**:

.. code:: python

	import myapi.views.homepage
	import myapi.views.users 
	import myapi.views.login


Now to implement the new view:

.. code:: python

	from luxon import register ,db
	from luxon.exceptions import AccessDeniedError
	from luxon.utils.password import valid


	@register.resource(['GET','POST'],'/login')
	def login(req,resp):

		# get the username and password from the request object
		username = req.json.get('username')
		req_password = req.json.get('password')

		# sql query that will return the password from the database for the given user
		sql = "SELECT id, password, role FROM user WHERE username = %s"

		# connection to database 
		with db() as conn:

			# cursor obj to execute our sql query with given username
			crsr = conn.execute(sql,(username,))
			# fetch result from cursor object
			result = crsr.fetchone()

		if result is None:
			raise AccessDeniedError("User not found")

		# password from database
		db_password = result['password']

		#validate the hashed password from dadabase with given password
		if not valid(req_password,db_password):	
			raise AccessDeniedError("Wrong password")

		# now that the login details have been validated
		# we can create the user credentials which will include:
		# the username, user id, user role, token and token expiry time
		req.credentials.new(result['id'], username)
		# add the user's role to the token 
		req.credentials.roles = result['role']
		# return the token 
		return req.credentials	

Restart the server so we can test our *login* view.
To test the login we'll create a POST request to "http://127.0.0.1:8000/login" and send the following body:

.. code:: json

	{
		"username":"Ricky T Dunigan",
		"password":"hypnotizeminds"

	}

The password we sent matches the password for that user in the database so we get the user's credentials back: all the
user details along with a token as well as a new "expire" field, which is the time when the token will expire. For more
about Luxon's password hashing have a look :ref:`Here<passwords>`

.. code:: json

	{
	    "username": "Ricky T Dunigan",
	    "user_id": "0e1462d5-f20d-4d69-8546-df549c127f90",
	    "expire": "2018/05/30 14:22:42",
	    "roles": [
		"admin"
	    ],
	    "token": "NfRXlCnD3M2GD56aZacFz0w34pBaa1SSWE9lK09HYUpkrmjwxDjN2uoL8qkl90+kdSbDB3qYjovelpWNlsfofqLkbFQ1jqtsHiXAwf9c5w0k5CpjY79t82IMIdXC3I6WuS1HLW/1Ozg/NpiHkRqbukhCnEVYSoIhjgBDbsQzsn7LNTIkYKMSRFcLkvK0KQW8+U/m2cme/3vl0UezF8qyKjt6JmMN1EzflFJSEfMb08pXWcy45FlcqNNJQpfu882I60tDgmkS6ryFUNo/qT1VtdKzCDcr8kipz4BwXc+h8t44k/gT2kY3/Gjfr9Cb34i4MQG926+gRmEzuofwNNp7WZ9MUDkPpYbOmif+J79jAsjqXs5WIj3xjvnP3TVFEkW7qF8DjdUgjihq2DgKNhTbXSm9HtoUNacL2wFma6jsg21XsoDheJl+O4XB+Yr9ZqKdAimE1KSIwMuAdceeEpa/IAXks0VeiJl/U7+ktMhqPw8mBP/cwtjUsPCCZ5Vkri/+d8AqFpbhNjmSjNfDCEVMw/H4Nw5hr6yA6GKRBVPNjFxc3Zd92r59KtjvswQ2g8d2duo2zUjfg9wSGnAJNhhBd3Ki60cQrAaYuL35WFHHSpt4raveiD7x02SFde2QUxZwwV+dDXZyzTR0jcikup6AAlbshc6mBQXXZB0/d0GOr2o=!!!!eyJyb2xlcyI6IFsiQURNSU4iXSwgImV4cGlyZSI6ICIyMDE4LzA1LzMwIDE0OjIyOjQyIiwgInVzZXJuYW1lIjogIlJpY2t5IFQgRHVuaWdhbiIsICJ1c2VyX2lkIjogIjBlMTQ2MmQ1LWYyMGQtNGQ2OS04NTQ2LWRmNTQ5YzEyN2Y5MCJ9"
	}
	

Part 9: Securing views with RBAC
--------------------------------
Luxon offers the ability to protect views based on users' roles, aka Role Based Access Control (RBAC).

This is done by tagged a view with with a rule. Only users assigned
with roles that match the rule assigned to the view, can access that view.
The roles and their associated rules are defined in the **myapi/policy.json** file. This was created when we set up the
package:

.. code:: json

	{
		"role:admin": "'admin' in req.credentials.roles",
		"role:user": "'user' in req.credentials.roles",
		"admin_view": "$role:admin",
		"user_view": "$role:admin or $role:user"
	}

These rules and roles are executed as python statements. For example, the ``admin_view`` rule will be expanded to ``True``, if
the ``role:admin`` role expands to ``True``. And the ``role:admin`` role will expand to ``True`` if the python statement
``'admin' in req.credentials.roles`` expands to ``True``.

To protect the `User` views with role based access, simply add a tag as an argument to every User view in
**views/users.py**

.. code:: python

		
    def __init__(self):
        router.add('POST','/create', self.create, tag='admin_view')
        router.add('GET','/users', self.users, tag='user_view')
        router.add('GET','/user/{id}', self.user, tag='user_view')
        router.add(['PUT','PATCH'],'/user/{id}', self.update, tag='admin_view')
        router.add('DELETE','/user/{id}', self.delete, tag='admin_view')

Now only users with the *admin* role assigned to them can make calls to the *create*, *update* and *delete* views,
that's to say all the views that write to the database. A user with the *user* role can access the views which only
read from the database. A user with the *admin* role can also access views with the *user* tag.

Right, now our API is secure. Remember to restart the server so these changes take effect.
We already have a user "Ricky T Dunigan", with the admin role, that we can log in as. Once we logged in with him and
received a Token we can use it to access the *create* view. Create a POST request with "http://127.0.0.1:8000/create"
in the *request URL* bar same as before. All we need to do is add a header. Put "X-Auth-Token" in the *key* field
and paste the Token into the *value* field.

Create another user with a *user* role instead of *admin* and repeat the same process of adding a header to the request.

Doing this with ``curl`` will look like:

.. code:: bash

    $ # Log in and get the token:
    $ token=$(curl -d ‘{"username": "Ricky T Dunigan", password": "hypnotizeminds"}’ http://localhost:8000/login | grep token | awk -F \" '{print $4}')
    $ curl -H "X-Auth-Token:$token" -d {"username": "user2", "password": "pass", "role": "user"} http://localhost:8000/create

This user will not be able to access the *create* view etc..



