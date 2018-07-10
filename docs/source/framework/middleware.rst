.. _middleware:

Middleware
==========

Global Middleware
-----------------

Middleware components provide a way to execute logic before the framework routes each request, after each request is routed but before the target responder is called, or just before the response is returned for each request. Components are registered with luxon.register_middleware(middle_class) function.

Note:
    This middleware is global for the application and runs on each processed request.

**Example of Middleware**

.. code:: python

	class ExampleMiddleware(object):
		def pre(self, req, resp):
			"""Processed before routing.

			Args:
				req: Request object that will eventually be
					provided to a responder.
				resp: Response object that will be provided to
					the responder.
			"""

		def resource(self, req, resp):
			"""Processed after routing.

			Args:
				req: Request object that will eventually be
					provided to a responder.
				resp: Response object that will be provided to
					the responder.
			"""

		def post(self, req, resp):
			"""Processed after responder.

			Args:
				req: Request object that will eventually be
					provided to a responder.
				resp: Response object that will be provided to
					the responder.
			"""

Responder Middleware
--------------------

There is a convenient utility decorator provided to add middleware responder(s) per responder.

**Example**

.. code:: python

	from luxon import register

	# Your middleware for specific responders.
	def middleware(req, resp, **kwargs):
		pass

	@register.resource('GET', '/')
	@register.middleware(middleware)
	def resource(req, resp, **kwargs):
		pass

