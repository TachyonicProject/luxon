.. _routing:

Routing
=======

Luxon routes incoming requests to resources based on a route path defined. The paths are defined for routes differently depending on the responder type. There are two types of responders:

	* Responder Class known as Resources.
	* Function known as Resource.

If the path requested by the client matches the template for a given route, the request is then passed on to the associated responder for processing. This responder then returns relevant payload.

If no route matches the request, then **luxon.exceptions.NotFound** is raised. This will result in sending a 404 response back to the client.

Note: The router is global for application.

The router supports three types of route expressions:
	* Standard: *'/' or '/page/page'*
	* Keyword Expression: *'/users/{domain}/{id}'*
	* Regex: *'regex:^/users.*$'*

**Standard Routes**
Stanard routes are faster and simply a dictionary lookup routine. It automatically trims '/' from route for more predictive matching.

**Keyword Expression Routes**
These are pretty fast and scaleable using compiled router. A field expression consists of a bracketed field name. For example '/users/{domain}/{id}'

These are provided as kwargs to the responder.

**Regex Routes**
These routes solves specific requirements. However they do not provide keyword arguements at this point to the responder.
Please note that regex routes are far slower than 'Standerd Routes' or 'Keyword Expression Routes'. They should only be used if deemed absolutly neccesary. They slow down the more they are used. In reality if these route matches are determined by scanning through a list until the compiled RE expression has found a match. Hence some cases order will be important.

However if you only use a couple of these, there will be no major performance impact. They are also only validated once 'Standard routes' and 'Keyword Expression routes' have found no matches. Hence it will NOT impact on performance of other route types.

Regex route follows the format of 'regex:expression'. Its important that 'regex:' is prepended since its used to determine the processing needed for the route.

Refer to :ref:`Responders <responders>` for a usage example.


Router Class
-------------
.. autoclass:: luxon.core.router.Router
   :members:

Luxon uses external code from the Falcon WSGI library for some router operations.
To view the license please refer to :ref:`f_license`

Compiled Router
----------------
.. autoclass:: luxon.ext.falcon.compiled.CompiledRouter
   :members:

Converter Dictionary
---------------------
.. autoclass:: luxon.ext.falcon.compiled.ConverterDict
   :members:

Options
--------------
.. autoclass:: luxon.ext.falcon.compiled.CompiledRouterOptions
   :members:


Converters
---------------
.. automodule:: luxon.ext.falcon.converters
   :members:



