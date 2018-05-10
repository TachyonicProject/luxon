.. _responders:

Responders
==========

Luxon uses Python functions or methods to represent resources. In practice, these act as controllers in your application. They convert an incoming request into one or more internal actions, and then compose a response back to the client based on the results of those actions. You can also stream by returning a custom iterable or file like object.

Each Responder and Middleware is provided with two arguements first:

	* Request Object for handler.
	* Response Object for handler.
	* Any kwargs provided by Router.

Responders can be referred to as the 'views'. These can be:

    * Group of responders. (This is a class with responders as methods)
    * Single responder. (This is a single function responder)

We internally refer to responders as resources and register them via resource decorators.

Single Responder
----------------

.. code:: python

    from luxon import g
    from luxom import register_resource

    # The last arguement is a keyword arguement known as tag. 
    # It is not needed. However when provided can be used by 
    # RBAC Policy engine to provide acccess control.
    @register_resource('GET', '/v1/user/{user_id}', 'admin')
    def user(self, req, resp, user_id):
        return 'user details'

Group Responders
----------------

.. code:: python

    from luxon import g
    from luxom import register_resources

    @register_resources()
    class Users(object):
        def __init__(self):
            # The last arguement is a keyword arguement known as tag. 
            # It is not needed. However when provided can be used by 
            # RBAC Policy engine to provide acccess control.
            g.router.add('GET', '/v1/user/{user_id}', self.user, 'admin')
            g.router.add('PATCH', '/v1/user/{user_id}', self.user, 'admin')
            g.router.add('DELETE', '/v1/user/{user_id}', self.user, 'admin')

        def user(self, req, resp, user_id):
            return 'user details'

        def edit(self, req, resp, user_id):
            pass

        def delete(self, req, resp, user_id):
            pass

Returning Data
--------------
The responder can either return data or write data to the response object provided.

Writing data is simply doing:

.. code:: python

    resp.write('hello world')

The response object behaves exactly like a file, and middleware can write data to it as well.

**If you simply return data, the following types are supported**:
    * ordereddict - Translated to JSON and content-type set automatically.
    * list - Translated to JSON and content-type set automatically.
    * dict - Translated to JSON and content-type set automatically.
    * str - Translated encoded UTF-8 bytes, handler sets default content type.
    * bytes - Returned and no translation takes place.
    * object - If object has to_json() method it will be used.
    * file - Returned and no translation takes place.

You can define the content type yourself in middleware or per resource before
returning any data. The content-type referes to mime format:

    e.g. *application/xml; charset=utf-8*

Warning:
    Please note written data using write method is overrided by returning data.
