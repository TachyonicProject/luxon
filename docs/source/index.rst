Welcome to Luxon Framework documentation!
=========================================

Release v\ |version| (:ref:`Installation <install>`)

About this project
------------------

The project is in 'Alpha' phase, some of the documentation and functionality is under-way.

Luxon Framework is a flexible Python application framework for rapid development. It's free and open source and before you ask: It's BSD Licensed! Contributions and contributors are welcome!

The project forms part of the Tachyonic Project which purpose is to build highly scaleable applications. The focus areas are fast deployment of customer portal, telemetry, billing, provisioing and complete orchastration of services.

**All functionality is maintained by REST-API interfaces and WEB driven by WSGI handler, worker daemons by minion handler, scripting envrionment and finally a cli interface.** 

End goal is to provide common interfaces for developing functionality for views. This common interface is provided by Luxon.

All responders have a common interface receiving request, response objects. Keyword arguements are provided to the responders based on the route used.

How is Luxon Different?
-----------------------
Luxon was designed to support demanding needs of large-scale services and 
responsive applications. Luxon provides many of the required day to day 
utilities, interfaces and helpers yet they cleanly implemented and the 
additional functionality does not utilize any resources unless required. In
general it complements any python projects by providing a bare-metal
performance, reliability and flexibility where you need it. 

More functionality on same hardware and more requests per second. We go through
great lengths to avoid introducing breaking changes and when we do they will be
fully documented. 

Luxon finally leaves a lot of the design decisions and implementation details
to you. You have the freedom to cusomize and tune the environment. 

Complete logging facility that solves many of the questions raised by many
developers on other similiar frameworks. Middleware or request views can append
information to logs that are only relevant to the current request. Such as
username etc. All requests are tagged with an ID which can be used to traceback
user related errors. 


Documentation
-------------

.. toctree::
   :maxdepth: 2

   license
   install
   framework/index
   wsgi/index
   minion/index
   script/index
   cli/index
   helpers/index
   utils/index
   community/index
   structs/index
   
