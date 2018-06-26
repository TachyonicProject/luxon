.. _webapp_tut:

================
Web App Tutorial
================

In this tutorial we will walk through building a simple web interface with Luxon. The same principles that were used
to build the API will be used, with different methods and responder code. Luxon provides many powerful tools that will
make every step of the process more convenient.
If you have not already installed Luxon you will need to do so: :ref:`Installation<install>`

This tutorial follows on the :ref:`api_tut`, eventually we will write responders that will communicate with the API.
That way we avoid double work. The API that we have already coded will handle the database etc. The Web App will
interface between a user and the API so the user will be exposed to the API via rendered HTML rather than direct API
calls. This tutorial assumes some dependencies are installed as per the :ref:`api_tut`.

At the end of this tutorial, you will have a working Web application, including a navigation menu,
where you can log in, and create, view, modify and delete users.

Similarly to the API tutorial we will start by setting up and deploying a package.

Part 1: Setting up a Python Package
-----------------------------------

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

    application = Wsgi(__name__, content_type='text/html; charset=utf-8')

    from myapp import views

Luxon's default content_type is ``'application/json'``. Here we specify the default content type as
``'text/html; charset=utf-8'`` because we are building an HTTP Web App.

You can read more about Luxon's Wsgi handler :ref:`Here<wsgi_hand>`

We also need to add a **static** directory which Luxon will copy over to the Project. Later we will use it to house the
static content for our server.

.. code:: bash
	
	$ mkdir myapp/static
	$ touch myapp/static/empty

We can now install our package, let's use pip's *-e* switch which will install it with an egg link, this will allow us
to edit the source code after the installation.

.. code:: bash
	
	$ pip3 install -e .

Part 2: Deploying a Python package with Luxon
---------------------------------------------

Now that we have our package installed as python library and we can deploy it as we would on server.

Let's create a project directory named *app* next to our *myapp* package directory, in the *app* directory we will
make another *myapp* directory in which to deploy *myapp*:

.. code:: bash

	$ cd ..
	$ mkdir app
	$ cd app 
	$ mkdir myapp

Everything is now set up for us to deploy our package with Luxon:

.. code:: bash 

	$ luxon -i myapp myapp 

This does a number of things, it copies over the **policy.json**, **settings.ini**, and **wsgi.py** files from the
`package` directory as well as creating **templates** and **tmp** directories inside **myapp**. The **tmp** directory
is where all the session data will live. The **templates** directory can house several *html* templates which can
overwrite templates from the package. We won't actually write any code in the project directory, all of that will still
happen in the package directory. We will however launch the webserver from the `deployment` directory.

We can't yet test if our project was successfully deployed however because we still need to create the *views* module
which the **wsgi.py** file imports. We will implement that module in the next step.

We are simultaneously using two directories, one for the `package` and one for the `project`. We will mostly be working
in the package directory to write code but we will be going back to the project directory to start the server.
Make sure not to get confused between the two. Before we move on let's review what the directory structure looks like at
this point:

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
	 
We are finally ready to start working on the Web Application! Leave this terminal open to launch the webserver in
future and open a new one in the `package` directory.

Part 3: Homepage View
---------------------
	 
Now we can start building our Web App by creating a homepage view. The views will exist as their own module in the
package. Let's create the module in our package directory at: **myapp/myapp**

.. code:: bash

	mkdir views
	touch views/__init__.py
	
To start off we will create a simple view that will respond to a "GET" request to the homepage "/".

.. code:: bash

	touch views/home.py

We will implement the view as a class in **views/home.py**.

.. code:: python
	
	from luxon import register, render_template, router

	@register.resources()
	class home():
		# define the route
		def __init__(self):
			router.add(('GET'), '/', self.home)

		# define the view 
		def home(self, req, resp):
			# return a pretty html template
			return render_template('myapp/home.html', title="My Web App")

And import the view in **views/__init__.py**:

.. code:: python

	import myapp.views.home

As you can see the main difference between the Web App homepage view and the API homepage view is that we return
HTML, instead of a JSON object. We could have simply returned the HTML as a string, but using templates will help
keep your code tidy and readable by separating the python from HTML. This is made easy by using Luxon's
``render_template`` function [#jinja]_. The first argument is the template to render (application name + '/' +
the name of the template). Thereafter all arguments function as variables that can be used in the template.

Of course for this to work we must first write the HTML which our view returns.

Create *templates* directory in our *package* directory to house the HTML templates that we will serve.
(Note that the name of this directory was omitted when we called the ``render_template`` function. Luxon knows to
locate templates in the *templates* directory of the *package*) [#template_override]_


For the home view we will return a template called ``home.html``, but to avoid double work, we'll create a base
template that will contain all the static boilerplate HTML that should be present on all pages. The we can create
a custom **.html** file for every subsequent view that needs to return one.

.. code:: bash

	$ mkdir templates
	$ touch templates/base.html
	$ touch templates/home.html

Populate ``base.html`` file with:

.. code:: html

    <html>
        <head>
            <title>{{ title }}</title>
        </head>
        <body>
            {% block body %}
            {% endblock %}
        </body>
    </html>

Here you can see the ``{{ title }}`` variable, that can be customised for each page by calling the template with the
``title="Some Title"`` argument.

The ``body`` block will be populated at this position when we extend this template from other templates.

The HTML template that the homepage view responds with will go in **templates/home.html**, we'll keep the code simple:

.. code:: html

    {% extends "myapp/base.html" %}
    {% block body %}
    <h1>Welcome to my Web Application</h1>
    {% endblock %}

`Jinja2 <http://jinja.pocoo.org/docs/2.10/>`_ is pretty self explanatory - *extend the "base.html" template. Populate the "body" block with this html*

Now we can test the view. Launch the webserver from the terminal open in our *app* directory.

.. code:: bash

	$ luxon -s --ip 127.0.0.1 --port 8001 myapp

When we browse over to http://127.0.0.1:8001 we should see our HTML homepage in all it's glory.

`Bootstrap <https://getbootstrap.com/>`_ is a javascript and css framework that gives nice responsive views. We will be
using some of its components, so let's update **templates/base.html** with:

.. code:: html

    <html>
        <head>
            <title>{{ title }}</title>
            <!-- Bootstrap core CSS -->
    	    <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            {% block body %}
            {% endblock %}
            <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"></script>
        </body>
    </html>

Part 4: Logging in
------------------
Next up we'll add a login page. Cancel the running web server with ctrl-c.

We can use user Bootstrap's `example login form <https://getbootstrap.com/docs/4.1/examples/sign-in/>`_, but with
username instead of email.

Create a login template at **templates/login.html** and enter the HTML:

.. code:: html

    {% extends 'myapp/base.html' %}
    {% block body %}
        <div class="row">
            <div class="col-md-3 offset-md-4">
                <form class="form-signin" method="post">
                  <h1 class="h3 mb-3 font-weight-normal">Please sign in</h1>
                  <label for="inputUser" class="sr-only">username</label>
                  <input type="text" name="username" class="form-control" placeholder="username" required autofocus>
                  <label for="inputPassword" class="sr-only">Password</label>
                  <input type="password" name="password" class="form-control" placeholder="Password" required>
                  <div class="checkbox mb-3">
                    <label>
                      <input type="checkbox" value="remember-me"> Remember me
                    </label>
                  </div>
                  <button class="btn btn-lg btn-primary btn-block" type="submit">Sign in</button>
                  <p class="mt-5 mb-3 text-muted">&copy; 2017-2018</p>
                </form>
            </div>
        </div>
    {% endblock %}


Now we'll create a view that loads this template. The view should be displayed when we do a **GET** on ``/login``.
Create **myapp/myapp/views/login.py** with:

.. code:: python

    from luxon import register, render_template, router

    @register.resources()
    class login():
        def __init__(self):
            router.add('GET','/login', self.login)

        def login(self,req,resp):
            return render_template('myapp/login.html', title="Login")

and import the view in **myapp/views/__init__.py**:

.. code:: python

    import myapp.views.home
    import myapp.views.login


This should render a nice login page when you visit http://localhost:8001/login, if you have restarted the server
with ``luxon -s`` again.

When the form is submitted, we wil receive a **POST** at ``/login``. We'll process both methods on the same view,
and respond accordingly. The data sent by submitting the form is available to us as a dict in the request's
``req.form_dict`` attribute. Luxon comes with an HTTP client that we can use to send requests to our API. So when our web app receives data from the browser, it will make a new request to the API to pass this data along.

Modify **myapp/myapp/views/login.py** with:

.. code:: python

    from luxon import register, render_template, router
    from luxon.utils.http import Client

    @register.resources()
    class login():
        def __init__(self):
            router.add(('GET','POST'),'/login',self.login)

        def login(self,req,resp):
            if req.method == 'GET':
                return render_template('myapp/login.html',title="Login")
            elif req.method == 'POST':
                api = Client()
                # Perform the login against our API
                login = api.execute('POST',
                                    'http://localhost:8000/login',
                                    data=req.form_dict)
                if 'token' in login.json:
                    token = login.json['token']
                    req.user_token = token
                    req.session['domain'] = "default"
                    req.session['tenant_id'] = "default"
                    req.session.save()
                resp.redirect('/')

Luxon's HTTP Client returns a luxon response object. Because our API returns JSON formatted data, we can access
it as a dict from the response's ``.json`` attribute. Of course, when the login is successful, we'll receive a
token in the response. We update the ``req.user_token`` attribute with this value. This will save the user's token
in the current :ref:`session<base_session>` so that we can use it for future requests as well. Luxon also caters
for session `domain` s and `tenant` s, but this is beyond the scope of this tutorial, so they are set to ``default``.
Lastly, the session is saved to persist this data, and we redirect the user to the home page.

At this point, you should be able to successfully log in with a user account that you created in the API tutorial.

Of course to test this you would have to go to the directory where you deployed the API and launch it on port 8000, as per the instructions in the previous tutorial.

While we're at it, let's also provide a view to log out. The final version of our **myapp/myapp/views/login.py** file
should look like this:

.. code:: python

    from luxon import register, render_template, router
    from luxon.utils.http import Client

    @register.resources()
    class login():
        def __init__(self):
            router.add(('GET','POST'), '/login', self.login)
            router.add('GET', '/logout', self.logout)

        def login(self, req, resp):
            if req.method == 'GET':
                return render_template('myapp/login.html',title="Login")
            elif req.method == 'POST':
                api = Client()
                # Perform the login against our API
                login = api.execute('POST',
                                    'http://localhost:8000/login',
                                    data=req.form_dict)
                if 'token' in login.json:
                    token = login.json['token']
                    req.user_token = token
                    req.session['domain'] = "default"
                    req.session['tenant_id'] = "default"
                    req.session.save()
                resp.redirect('/')

        def logout(self, req, resp):
            req.user_token = None
            resp.redirect('/login')


Part 5: Navigation Menu
------------------------

Bootstrap gives us a nice `navigation bar <https://getbootstrap.com/docs/4.0/components/navbar/>`_ that we can use for
a menu. Update the **templates/base.html** template with the ``{% include %}`` statement to add the menu at the top
of the page:

.. code:: HTML

    <html>
        <head>
            <title>{{ title }}</title>
            <!-- Bootstrap core CSS -->
            <link href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/css/bootstrap.min.css" rel="stylesheet">
        </head>
        <body>
            {% include "myapp/navbar.html" %}
            {% block body %}
            {% endblock %}
            <script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
            <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.1/js/bootstrap.min.js"></script>
        </body>
    </html>

Create the the **myapp/templates/navbar.html** template:

.. code:: HTML

    <nav class="navbar navbar-expand-lg navbar-light bg-light">
      <a class="navbar-brand" href="/">Home</a>
      <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarSupportedContent">
        <ul class="navbar-nav mr-auto">
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
              Users
            </a>
            <div class="dropdown-menu" aria-labelledby="navbarDropdown">
              <a class="dropdown-item" href="/users">View</a>
              <a class="dropdown-item" href="/user/add">Add</a>
            </div>
          </li>
          <li class="nav-item">
              {% if REQ.user_token %}
              <a class="nav-link" href="/logout">Logout</a>
              {% else %}
              <a class="nav-link" href="/login">Login</a>
              {% endif %}
          </li>
        </ul>
      </div>
    </nav>

Notice that luxon provides the request object to the jinja environment, in a variable called ``REQ``, so we look at
``REQ.user_token`` to see if the user is logged in or not, and depending on that, either display *login* or *logout* in
the menu.

In our menu we are referencing two views we have not yet created - ``/users`` and ``/user/add``. These will be created
in the next two sections.

Part 6: Listing Users
---------------------

In this part we create a view to list the users currently in the database. We obtain the list by making a call
to the ``/users`` view on our API.

First we'll create a template to render the users. Create **templates/users.html** and populate it with:

.. code:: HTML

	{% extends "myapp/base.html" %}
	{% block body %}
	<table class="table table-hover">
	    <thead>
		<tr>
		    <th>
		        Username
		    </th>
		    <th>
		        Role
		    </th>
		    <th>
		        Edit
		    </th>
		    <th>
		        Delete
		    </th>
		</tr>
	    </thead>
	    <tbody>
		{% for user in users %}
		    <tr>
		        <td>{{ user.username }}</td>
		        <td>{{ user.role }}</td>
		        <td><a href="/user/edit/{{ user.id }}">-</a></td>
		        <td><a href="/user/delete/{{ user.id }}">X</a></td>
		    </tr>
		{% endfor %}
	    </tbody>
	</table>
	{% endblock %}

To render this template, we'll need to pass a list variable called ``users`` to iterate through. We've added an option
to delete the user so long, we will create responders for the ``user/delete/{id}`` and ``user/edit/{id}`` views later.

Next up we create the view. Create **views/users.py** with:

.. code:: python

    from luxon import register, render_template, router
    from luxon.utils.http import Client

    api = Client('http://localhost:8000')

    @register.resources()
    class users():
        def __init__(self):
            router.add('GET', '/users', self.list)

        def list(self, req, resp):
            users = api.execute('GET', '/users')
            return render_template('myapp/users.html', users=users.json, title="Users")

In the API tutorial we protected our ``/users`` view with a tag, so this means we need to supply the token
to the API so that it can authorize the logged-in user. If this is set in the session in the request's ``user_token``
attribute (like we did inside the ``/login`` view), luxon includes this value for the ``X-Auth-Token`` header when
making the request to the API. The resulting list of users we obtain from the response's ``.json`` attribute, and pass
that to the template in the variable ``users``.

Import this view: update **views/__init__.py**:

.. code:: python

    import myapp.views.home
    import myapp.views.login
    import myapp.views.users

Part 7: Adding a User
----------------------

In this part we'll create a view to add new users. Once again, we'll start with the template. Create
**templates/add_user.html** with:

.. code:: HTML

    {% extends "myapp/base.html" %}
    {% block body %}
        <div class="row">
            <div class="col-md-4 offset-md-4">
                <form method="post">
                    {{ form }}
                    <button type="submit" class="btn btn-primary">Create</button>
                    <a class="btn btn-secondary" href="/" role="button">Cancel</a>
                </form>
            </div>
        </div>
    {% endblock %}

We will render this template on the ``/user/add`` view for the **GET** method. Just like the login page, when we submit
this form, we will receive a call to the same view for a **POST**.

This time we add both methods in one go. Update **views/users.py** to:

.. code:: python

    from luxon import register, render_template, router
    from myapi.models.user import User
    from luxon.utils.bootstrap4 import form
    from luxon.utils.http import Client

    api = Client('http://localhost:8000')

    @register.resources()
    class users():
        def __init__(self):
            router.add('GET', '/users', self.list)
            router.add(('GET', 'POST'), '/user/add', self.add)

        def list(self, req, resp):
            users = api.execute('GET', '/users')
            return render_template('myapp/users.html', users=users.json, title="Users")

        def add(self, req, resp):
            if req.method == 'GET':
                user_form = form(User)
                return render_template('myapp/add_user.html',form=user_form, title="Add User")
            elif req.method == 'POST':
                api.execute("POST", "/create", data=req.form_dict)
                resp.redirect('/users')


Notice that we import the exact same model as the API did. We use luxon's ``luxon.utils.bootstrap4.form`` function
to convert the model in to a responsive HTML form. How convenient! No DRY'ing (DRY = Dont Repeat Yourself).

Just like for the login view, when the request comes via the **POST** method, we simply create a new **POST** request
to our API, with the received form data (``req.form_dict``) as the POST ``data``. After the user has been created,
we redirect back to the list of users at ``/users``.

Running your application with ``luxon -s`` should now have views for all the menu entries, you should be able
to view a list of existing users, and also be able to create a new user.


Part 8: Deleting or Editing a user
------------------------------------

Our last task is to provide the options to delete and edit users. We don't need a template to do this, we'll simply
look out for a **GET** on ``/user/delete/{id}``, and then create a **DELETE** request to our API on ``/user/{id}``.

The Edit view will work similarly to the Add User view, and use the same template **add_user** template. First a 'GET' request will return a form populated by the user in question's user info, using luxon's form utility. Then a "PUT" call is made to the API to edit the user with updated info.

The final version of our **views/users.py** looks like this:


.. code:: python

	from luxon import register, render_template, router
	from myapi.models.user import User
	from luxon.utils.bootstrap4 import form
	from luxon.utils.http import Client

	api = Client('http://localhost:8000')

	@register.resources()
	class users():
	    def __init__(self):
		router.add('GET', '/users', self.list)
		router.add(('GET', 'POST'), '/user/add', self.add)
		router.add('GET', '/user/delete/{id}', self.delete)
		router.add(('GET','POST'),'/user/edit/{id}',self.edit)

	    def list(self, req, resp):
		users = api.execute('GET', '/users')
		return render_template('myapp/users.html', users=users.json, title="Users")

	    def add(self, req, resp):
		if req.method == 'GET':
		    user_form = form(User)
		    return render_template('myapp/add_user.html',form=user_form, title="Add User")
		elif req.method == 'POST':
		    api.execute("POST", "/create", data=req.form_dict)
		    resp.redirect('/users')

	    def delete(self, req, resp, id):
		    api.execute("DELETE", "/user/"+id)
		    resp.redirect('/users')

	    def edit(self,req,resp,id):
		usr = api.execute("GET","/user/"+id)

		if req.method == 'GET':
		    user_form = form(User,usr.json)
		    return render_template('myapp/add_user.html',form=user_form, title="Edit User")

		elif req.method == 'POST':
		    api.execute("PUT","/user/"+id,data=req.form_dict)
		    resp.redirect('/users')


And there you have it, a Web Front end for your API.

.. rubric:: Footnotes

.. [#jinja] The ``render_template`` function is a convenient wrapper that makes use of `jinja2 <http://jinja.pocoo.org/docs>`_ templates
.. [#template_override] This directory is distinct from the *templates* directory in the *app* directory. If one places templates in the *app/templates* directory, they take precedence over the ones in the *package/templates* directory.










