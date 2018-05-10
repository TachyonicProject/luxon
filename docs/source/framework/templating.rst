.. _templating:

Templating
==========

Luxon provides templating engine interface to Jinja2. Our interface only
inherits from Jinja2 and extends the functionality needed in the framework. The
loader will ensure that templates are found in the correct places.

There are two places for templates to exist:
    * Python package.
    * File system. These are known as overrides.

We have overrides so that users using your application can customize the
templates to be rendered.

By looking at the following example we will describe the process:

.. code:: python

    from luxon import render_template

    render_template('package/stuff/template.html', name='Foo')

The loader will first attempt to find the an override in the appplication root.
for example */var/www/app/templates/package/stuff/template.html.*

When there is no such template it will look import package.
for example it will look inside package: *templates/stuff/template.html*

**Direct interface**

You can use the templating engine directly with the templates by using
Environment class from luxon.core.template.

