.. _cmd_tut:

CMD Tutorial
============

In addition to WSGI responders, Luxon also offers the ability handle requests and responses via the command line.
In our :ref:`api_tut` we created a RESTful API with which we can log in, and manipulate user accounts. Our
:ref:`webapp_tut` then provided a Web User Interface through which we could do the same. In this tutorial, we will
build a command line tool that will allow us to list, create, modify and delete user accounts.

At the end of this tutorial, you will have a command line tool that shows you which methods are available via a
``-h`` help switch:

.. code:: bash

    $ mycmd -h
    usage: mycmd [-h] [-f | -k | -r | -d] [-a APP] [-p PID]
                 {add,update,list,delete} ...

    MyCMD

    positional arguments:
      {add,update,list,delete}
                            Methods
        add                 add resources
        update              update resources
        list                list resources
        delete              delete resources

    optional arguments:
      -h, --help            show this help message and exit
      -f, --fork            Fork Process
      -k, --kill            Stop/Kill Process
      -r, --restart         Restart Process
      -d, --debug           Debug
      -a APP, --app APP     Application Path
      -p PID, --pid PID     PID File

For each method, it will also show what options are available:

.. code:: bash

    $ mycmd add | tail -3

    routes for add:
        /user

And you will be able to be able to list users via ``mycmd list users``, add user with ``mycmd add user``, update users
with ``mycmd update user`` and delete users with ``mycmd delete user``.

Similarly to the API tutorial we will start by setting up and deploying a package.

For this tutorial to work, you must have completed the :ref:`api_tut`, and have an admin user account to log in with.


Part 1: Setting up a Python Package
-----------------------------------

Once again we need to create a python package that we can install as a pip library. Then we will be able to deploy the
package as a project which will host our executable command line client.

We will create the package in a *development* directory and then we will deploy the project in an *app* directory.

So on to the package, let's call it *mycmd*:

Create a working directory where we can develop the package, the actual code will go in an nested directory with the
same name :

.. code:: bash

	$ mkdir mycmd
	$ cd mycmd
	$ mkdir mycmd

In order to install the package we need a **setup.py** file in the top directory:

.. code:: bash

	$ touch setup.py

Let's keep the content of our **setup.py** as simple as possible:

.. code:: python

	from setuptools import setup

	setup(name = 'mycmd',
	      version = '0.01',
	      description = 'CMD Tutorial',
	      packages = ['mycmd'])

We also need a **__init__.py** file in the nested directory, we can leave it empty.

.. code:: bash

	$ touch mycmd/__init__.py

This is all we need for a simple python package, it is now installable. However before we install it we need to add a
few files that Luxon will need.

.. code:: bash

	$ touch mycmd/settings.ini
	$ touch mycmd/policy.json
	$ touch mycmd/wsgi.py


Luxon provides the ability to cache responses. For more info the caching options, refer to :ref:`caching`.
Update **settings.ini** with:

.. code::

    [application]
    name="MyCMD"

    [cache]
    backend = luxon.core.cache:Memory
    max_objects = 100
    max_object_size = 1000

    [myapi]
    url=http://localhost:8000
    user=Ricky T Dunigan
    pass=hypnotizeminds


In our API tutorial we protected our views with policies. In order to write to the database, we will have
to authenticate ourselves to the API. To make the process more convenient for the user, we
supply the login credentials in the **settings.ini** file, so that the user does not have to
type it in every time the command is run. Make sure you have the correct information entered here: address, port,
username and password.

Luxon's minimum requirement for a **policy.json** file is an empty JSON object:

.. code:: json

    {}

The **wsgi.py** file will automatically be copied to the `app` directory when we install our tool.
We are not using WSGI for this project, in fact, this file will become our command line tool.
For now populate it with the following, we will rename it once we have installed our tool:

.. code:: python

    #!/path/to/your/system/python3
    from luxon.core.handlers.cmd import Cmd

    application = Cmd(__name__)
    import mycmd.views

    application()

Make sure to have the correct /path/to/your/system/python3 in the first line (as can be obtained with the command
``which python3``), and make this file executable:

.. code:: bash

    $ chmod +x mycmd/wsgi.py


We are importing ``mycmd.views`` (even though we have not yet created them) as this is where the "routes" aka "required
arguments" aka "resources" for our command will be defined. And then simply execute the luxon ``Cmd`` object. You can
read more about Luxon's Command Line Responder :ref:`here<cmd_handler>`.

We can now install our package, let's use pip's *-e* switch which will install it with an egg link, this will allow us
to edit the source code after the installation.

.. code:: bash

	$ cd mycmd
	$ pip3 install -e .

Part 2: Deploying a Python package with Luxon
----------------------------------------------
Now that we have our package installed as python library we can deploy it as we would on a server.

Navigate to the project directory named *app* that we created for our previous tutorials. In the *app* directory we will
make a *mycmd* directory in which to deploy *mycmd*:

.. code:: bash

	$ cd ../app
	$ mkdir mycmd

Everything is now set up for us to deploy our package with Luxon:

.. code:: bash

	$ luxon -i mycmd mycmd

This will copy the necessary files to the project directory. Afterwards, the directory structure should look like:

.. code:: bash

    mycmd/
        setup.py
        mycmd/
            __init__.py
            policy.json
            settings.ini
            wsgi.py

    app/
        mycmd/
            tmp/
            templates/
                mycmd/
            policy.json
            settings.ini
            wsgi.py

Part 3: Preparing our Command Line Client
-----------------------------------------

We *could* use our wsgi.py in the **app/mycmd** dir script as-is, but typically one would give it a better name.
Let's call ours ``mycmd``:

.. code:: bash

    $ cd mycmd
    $ mv wsgi.py mycmd

Now we can run the command with ``./mycmd``. For convenience sake, let's make an alias to our command. If you have for
example created your **app** directory inside **/opt**, create an alias as such to the full path:

.. code:: bash

    $ alias mycmd='/opt/app/mycmd/mycmd'

Now you should be able to run the command ``mycmd`` from any directory:

.. code:: bash

    $ cd /tmp
    $ mycmd
    usage: mycmd [-h] [-f | -k | -r | -d] [-a APP] [-p PID] {} ...
    mycmd: error: the following arguments are required: method
    $ mycmd -h
    usage: mycmd [-h] [-f | -k | -r | -d] [-a APP] [-p PID] {} ...

    MyCMD

    positional arguments:
      {}                 Methods

    optional arguments:
      -h, --help         show this help message and exit
      -f, --fork         Fork Process
      -k, --kill         Stop/Kill Process
      -r, --restart      Restart Process
      -d, --debug        Debug
      -a APP, --app APP  Application Path
      -p PID, --pid PID  PID File

Note that this will not work yet because we have not yet implemented the **views** module that the **wsgi.py** file imports.

Because we protected our views with policy tags, we won't have access to them
unless the user authenticates first. For convenience sake, we'll allow the administrator to specify the login details
in the **settings.ini** file, as we did when creating the package:

.. code::

    [myapi]
    url=http://localhost:8000
    user=Ricky T Dunigan
    pass=hypnotizeminds

This will allow us write a little login helper function that grab these credentials and prepare the
headers for our api client:

.. code:: python

    from luxon import g
    from luxon.utils.http import Client

    config=g.app.config

    api_user = config.get('myapi','user')
    api_pass = config.get('myapi','pass')
    api = Client(config.get('myapi','url'))

    def login():
        login_data = {"username": api_user, "password": api_pass}
        result = api.execute('POST','/login', data=login_data)
        if 'token' in result.json:
            return {'X-Auth-Token': result.json['token']}

``g`` is the global luxon variable, it gives us access to the **settings.ini** file and many more.
You can read more about it :ref:`here<globals>`. ``luxon.utils.http.Client`` is luxon's same built-in http client
that we used in the :ref:`webapp_tut`. Read more about it :ref:`here <luxon_client>`.

Part 4: Creating the first Command argument - listing users
-----------------------------------------------------------

We provide options to the command in the exact same way as we provide views for luxon applications.
In our **package** **mycmd/mycmd** directory, create a directory **views** and add the __init__.py file:

.. code:: bash

    $ cd mycmd/mycmd
    $ mkdir views
    $ touch views/__init__.py

We are only going to create one view file, called **users.py**, which will house all our routes. Create it and import
it:

.. code:: bash

    $ touch views/users.py
    $ echo "import mycmd.views.users" >> views/__init__.py

We'll start of with the first view, one that will list all the existing users. We *could* let the view grab the list
of users straight from the database, but for the purpose of this tutorial, we show how you can do this
through the API. This allows one to deploy the system in a distributed fashion: users can run the commands even on
machines that do not have access to the database.

We want to retrieve a list of all users when we run the command ``mycmd list users``. In this case, ``list`` is the
method, and ``users`` is the view. Update **views/users.py** with:

.. code:: python

    import json
    from luxon import register, router
    from luxon.utils.http import Client
    from luxon import g

    config=g.app.config

    api_user = config.get('myapi','user')
    api_pass = config.get('myapi','pass')
    api = Client(config.get('myapi','url'))

    def login():
        login_data = {"username": api_user, "password": api_pass}
        result = api.execute('POST','/login', data=login_data)
        if 'token' in result.json:
            return {'X-Auth-Token': result.json['token']}

    @register.resources()
    class users():
        def __init__(self):
            router.add('LIST', 'users', self.list)

        def list(self, req, resp):
            users = api.execute('GET', '/users', headers=login())
            return json.dumps(users.json,indent=4) + '\n'

Notice we have added our code to include our helper function ``login()`` here.
Once again we decorate our class with ``@register.resources()``, exactly the same as in our Web and API tutorial, but
this time luxon registeres the routes and views as command arguments. When we run the command with arguments
``list users``, the ``list()`` method will be executed. This method simply executes a 'GET' request on our API at
"/users", providing a value for the ``X-Auth-Token`` that it obtained from our ``login()`` function.
The response is a luxon :ref:`wsgi_response` object, and since our API returns JSON data, we can access that
as a dict in the response's ``.json`` attribute. We convert this back into JSON formated text, which we return to the
user of the script.

Essentially all our CMD's functionality comes from making calls to our API, as in *myapp*, so keep in mind that for the 
CMD to work our API *myapi* will have to be running all the time on http://localhost:8000, or the url we specified in the
settings.ini file.

When you run your ``mycmd`` command with the ``-h`` switch again, you should see that it now shows that you require,
and have available, a positional argument called "list", which will "list resources".

.. code:: text

    positional arguments:
      {list}
                            Methods
        list                list resources

The resource we are interested in is of course "users".

If you run the command ``mycmd list`` without specifying a resource, you will see the help text displaying at the
bottom that a ``/users`` route is available for the ``list`` method.

.. code:: text

    routes for list:
        /users

And when you run ``mycmd list users``, you should see a list of users, currently present in your database, as returned
to you by your API.

.. note:: The luxon cmd responder allows for the option to be run as a daemon. As such, it requires to write a pid file inside the ``/var/run`` directory. On some systems, the permission on this directory belongs to the "daemon" group, and regular users won't be able to write to this directory. As such, we can update our alias to run our command as the "sudo" user:

.. code:: bash

    $ alias mycmd='sudo /opt/app/mycmd/mycmd'



Part 5: Adding new users
------------------------

In this Section we will be adding the view that allows us to add a new user account. Just like the WSGI handler,
luxon's cmd handler also works with request and reponse objects. The request object has a ``.read()`` method, that
reads from stdin. This gives us the opportunity to capture input from the user's terminal.

Update **views/users.py** with:

.. code:: python

    import json
    from luxon import register, router
    from luxon.utils.http import Client
    from luxon import g

    config=g.app.config

    api_user = config.get('myapi','user')
    api_pass = config.get('myapi','pass')
    api = Client(config.get('myapi','url'))

    def login():
        login_data = {"username": api_user, "password": api_pass}
        result = api.execute('POST','/login', data=login_data)
        if 'token' in result.json:
            return {'X-Auth-Token': result.json['token']}

    @register.resources()
    class users():
        def __init__(self):
            router.add('LIST', 'users', self.list)
            router.add('ADD', 'user', self.add)

        def list(self, req, resp):
            users = api.execute('GET', '/users', headers=login())
            return json.dumps(users.json,indent=4) + '\n'

        def add(self, req, resp):
            new_user = json.loads(req.read())
            user = api.execute("POST", "/create", headers=login(), data=new_user)
            return json.dumps(user.json,indent=4) + '\n'

Now our cmd has the ``add user`` option available. It will read from stdin, which we require to be valid JSON
data, exactly as we would create when POST'ing to the API. The ``add()`` method then loads this JSON
data as a dict, and executes a POST to the "/create" route on the API, using the received JSON data
as the POST body. We also return the reponse's body so that the user can see the result.

.. code:: bash

    $ mycmd add user
    Password: <Enter sudo password here>
    {"username": "anotheruser", "password": "somepass", "role":"user"}

In order to end the stdin stream, we press ctrl-d (might have to press it twice on some systems. On other systems
ctrl-z is used)

If the call was successfull, we should see a reponse with the UUID that was assigned to this user:

.. code:: bash

    $ mycmd add user
    Password: <Enter sudo password here>
    {"username": "anotheruser", "password": "somepass", "role":"user"}^d^d
    {
        "id": "bc22fc3c-8b6a-4eb9-85a2-5385af4743c5",
        "username": "anotheruser",
        "password": "$2b$12$3Ay47Fc4UBvXQ9EjKClPteJ.kPPO7SWzmpRrkw0PstYhClM5Pia3m",
        "role": "user"
    }

Part 6: Updating a user.
------------------------

Updating user accounts will be similair to adding new ones, except we have to provide an existing
UUID. The API call needs to be a PUT or PATCH to /user/{id}. We can grab the value for "id" from the
command argument, similair to how the API does it. We'll use the method "update" and route expression ``user={id}``,
so running the command will look like ``mycmd update user=some-uuid``

Update **views/users.py** with:

.. code:: python

    import json
    from luxon import register, router
    from luxon.utils.http import Client
    from luxon import g

    config=g.app.config

    api_user = config.get('myapi','user')
    api_pass = config.get('myapi','pass')
    api = Client(config.get('myapi','url'))

    def login():
        login_data = {"username": api_user, "password": api_pass}
        result = api.execute('POST','/login', data=login_data)
        if 'token' in result.json:
            return {'X-Auth-Token': result.json['token']}

    @register.resources()
    class users():
        def __init__(self):
            router.add('LIST', 'users', self.list)
            router.add('ADD', 'user', self.add)
            router.add('UPDATE', 'user={id}', self.edit)

        def list(self, req, resp):
            users = api.execute('GET', '/users', headers=login())
            return json.dumps(users.json,indent=4) + '\n'

        def add(self, req, resp):
            new_user = json.loads(req.read())
            user = api.execute("POST", "/create", headers=login(), data=new_user)
            return json.dumps(user.json,indent=4) + '\n'

        def edit(self, req, resp, id):
            update_user = json.loads(req.read())
            user = api.execute("PUT", "/user/"+id, headers=login(), data=update_user)
            return json.dumps(user.json,indent=4) + '\n'

Now we can modify users with our command's ``update user=`` argument:

.. code:: bash

    $ mycmd update user=bc22fc3c-8b6a-4eb9-85a2-5385af4743c5
    {"role": "admin"}

When hitting ctrl-d, we should see the response with the updated info from our API:

.. code:: bash

    $ mycmd update user=bc22fc3c-8b6a-4eb9-85a2-5385af4743c5
    {"role": "admin"}^d^d
    {
        "id": "bc22fc3c-8b6a-4eb9-85a2-5385af4743c5",
        "username": "anotheruser",
        "password": "$2b$12$3Ay47Fc4UBvXQ9EjKClPteJ.kPPO7SWzmpRrkw0PstYhClM5Pia3m",
        "role": "admin"
    }

Part 6: Deleting a user.
------------------------

Finally we provide the option to delete a user with the command ``mycmd delete user={id}``. We'll ``try`` to do
with with a DELETE method on the API, and if the request fails for some reason, we'll return the error to the user.

Update **views/users.py** with:

.. code:: python

    import json
    from luxon import register, router
    from luxon.utils.http import Client
    from luxon import g

    config=g.app.config

    api_user = config.get('myapi','user')
    api_pass = config.get('myapi','pass')
    api = Client(config.get('myapi','url'))

    def login():
        login_data = {"username": api_user, "password": api_pass}
        result = api.execute('POST','/login', data=login_data)
        if 'token' in result.json:
            return {'X-Auth-Token': result.json['token']}

    @register.resources()
    class users():
        def __init__(self):
            router.add('LIST', 'users', self.list)
            router.add('ADD', 'user', self.add)
            router.add('UPDATE', 'user={id}', self.edit)
            router.add('DELETE', 'user={id}', self.delete)

        def list(self, req, resp):
            users = api.execute('GET', '/users', headers=login())
            return json.dumps(users.json,indent=4) + '\n'

        def add(self, req, resp):
            new_user = json.loads(req.read())
            user = api.execute("POST", "/create", headers=login(), data=new_user)
            return json.dumps(user.json,indent=4) + '\n'

        def edit(self, req, resp, id):
            update_user = json.loads(req.read())
            user = api.execute("PUT", "/user/"+id, headers=login(), data=update_user)
            return json.dumps(user.json,indent=4) + '\n'

        def delete(self, req, resp, id):
            try:
                api.execute("DELETE", "/user/"+id, headers=login())
                return "User deleted\n"
            except Exception as e:
                return str(e) + '\n'

Now we can delete a user:

.. code:: bash

    $ mycmd delete user=bc22fc3c-8b6a-4eb9-85a2-5385af4743c5
    User deleted

This concludes the Command Line Tool tutorial.
