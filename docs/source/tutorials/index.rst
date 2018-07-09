.. _tuts:

===============
Luxon Tutorials
===============

Luxon can be used to build many types of applications. A common implementation is a Web Application that makes calls
to a RESTfull API application, that in turns performs tasks like running commands and updating a database.

The reason for this is for security purposes: Typically, the web application has to be available to the world, while
the back end API application can be placed behind a firewall for added protection, since it requires access to other
internal systems.

These different components have been broken up into separate tutorials. Once all of the tutorials have been completed,
the completed project will consist of:

    - A RESTFull API with views to Create, Read, Update and Delete (CRUD) users.
    - An HTTP Web user interface through which the same can be achieved.
    - A Command Line client through which the same can be achieved.
    - Models to interface with HTML Forms and MySQL databases.

The project will also have authentication and access control features:

    - The ability to assign roles to users.
    - The ability to tag responders with roles.
    - A policy to dictate which roles can access wich tags.

.. toctree::
    :maxdepth: 2
    
    api
    wsgi_web
    cmd
    minion
    
