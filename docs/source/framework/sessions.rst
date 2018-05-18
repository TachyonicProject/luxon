Sessions
============

Luxon comes with a session base class that can be used in end-points and modules to provide session handling as needed. Luxon allows for handling session data with Redis as well as files and cookies.

Base Class
-----------
.. autoclass:: luxon.core.session.session.Session
	:members:

Redis
---------
.. autoclass:: luxon.core.session.sessionredis.SessionRedis
	:members:

Files
-------
.. autoclass:: luxon.core.session.sessionfile.SessionFile
	:members:

Cookies
-----------

.. autoclass:: luxon.core.session.sessioncookie.SessionCookie
	:members:

Session authentication
------------------------

.. autoclass:: luxon.core.session.sessionauth.TrackToken
	:members:
