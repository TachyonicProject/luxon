Welcome to Luxon Framework documentation!
=========================================

Release v\ |version| (:ref:`Installation <install>`)

The project is in 'Alpha' phase, some of the documentation and functionality is under-way.

Luxon Framework is a flexible Python application framework for rapid development. It's free and open source and before you ask: It's BSD Licensed! Contributions and contributors are welcome!

The project forms part of the Tachyonic Project which purpose is to build highly scaleable applications. The focus areas are fast deployment of customer portal, telemetry, billing, provisioing and complete orchastration of services.

**All functionality is maintained by REST-API interfaces and WEB driven by WSGI handler, worker daemons by minion handler, scripting envrionment and finally a cli interface.** 

End goal is to provide common interfaces for developing functionality for views. This common interface is provided by Luxon.

All responders have a common interface receiving request, response objects. Keyword arguements are provided to the responders based on the route used.

Useful Links
------------

- `Website <http://www.tachyonic.org/>`_.
- `Github <https://github.com/TachyonicProject/luxon>`_.
- `Pypi <https://pypi.python.org/pypi/luxon>`_.

Documentation
-------------

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   framework/index
   wsgi/index
   minion/index
   script/index
   cli/index
   helpers/index
   utils/index
   community/index
   structs/index
   
