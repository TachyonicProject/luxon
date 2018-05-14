.. _structure:

Package Layout
==============
    * luxon/contrib 
	Contributed functionality for Luxon.

    * luxon/core 
	Core Luxon code.
    * luxon/core/cls 
	Generic base and meta-classes.
    * luxon/core/application.py 
	Base Application Class.
    * luxon/core/config 
	Luxon Config Parser.
    * luxon/core/globals.py 
	Global 'g' class.

    * luxon/core/handlers 
	Application Handlers.
    * luxon/core/handlers/cli 
	CLI Interface handler.
    * luxon/core/handlers/minion 
	Daemon/Worker Interface handler.
    * luxon/core/handlers/script 
	Script Interface handler.
    * luxon/core/handlers/wsgi 
	WSGI Interface handlers.

    * luxon/core/html 
	Low level html utils. e.g to generate menu.
    * luxon/core/policy 
	Policy RBAC Rule-Set Engine.
    * luxon/core/register.py 
	View / Class of views registration functions etc.
    * luxon/core/request.py 
	Base Client Request Object.
    * luxon/core/response.py 
	Base Response Object for Client Request.
    * luxon/core/template.py 
	Luxon wrapper for Jinja2 Template Environment.
    * luxon/core/helpers 
	Helper functions for consumers of framework.
    * luxon/core/middleware 
	Middleware included. e.g. Policy validator for views.
    * luxon/core/structs 
	Luxon data structures. e.g. Thread Local Dictionary.
    * luxon/core/testing 
	Utilities and helpers for Unit testing.
    * luxon/core/wsgi.py 
	Example WSGI file.
