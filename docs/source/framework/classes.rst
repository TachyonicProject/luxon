======================
Generic Classes
======================

Luxon offers a number of generic base classes and meta-classes that can be used to easily create custom classes as needed.

.. _nullerror:

NullError Class
===================

This class is useful if you want to create a temporary object that does not have any attributes yet. For example creating a request object before the request is actually sent. No opperations will be allowed on the object.

.. autoclass:: luxon.core.cls.nullerror.NullError
	:members:


.. _reproduce:

Reproduce Class
=================

.. autoclass:: luxon.core.cls.reproduce.Reproduce
	:members:
        :special-members:


.. _singleton:

Singleton Classes
===================

For when you want to create a single object or you want all objects to be identical

Thread Singleton
-----------------
.. autoclass:: luxon.core.cls.singleton.ThreadSingleton
	:members: 

Named Singleton
-----------------
.. autoclass:: luxon.core.cls.singleton.NamedSingleton
	:members: 


Singleton
-----------------
.. autoclass:: luxon.core.cls.singleton.Singleton
	:members: 
