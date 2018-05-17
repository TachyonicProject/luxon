.. _structure:

Package Layout
==============

This table serves as an exact index of the Luxon source code

Contributions
------------------------

========================================= ==============================================
luxon/contrib                             Contributed functionality for Luxon
========================================= ==============================================

Luxon Core
--------------

========================================= ==============================================
luxon/core				                  Core Modules
luxon/core/cache			  Memory caching classes
luxon/core/cls                            Generic base and meta-classes.
luxon/core/config                         Luxon Config Parser.
luxon/core/db                             Luxon Databases
luxon/core/handlers                       Application Handlers.
luxon/core/handlers/wsgi                  WSGI Interface handlers.
luxon/core/policy                         Policy RBAC Rule-Set Engine.
luxon/core/servers                        Luxon servers

luxon/core/auth.py                        PKI Authentication
luxon/core/globals.py                     Global 'g' class.
luxon/core/logger.py                      Logging service, for debugging etc...
luxon/core/regex.py                       Regex patterns
luxon/core/register.py                    Class of views/registration functions     
luxon/core/router.py                      Router Interface   
luxon/core/session.py                     Session data handling  
luxon/core/template.py                    Luxon wrapper for Jinja2 Template Environment
========================================= ==============================================

External Code
----------------

========================================= ==============================================
luxon/ext/falcon                          Routing converters and compilers
========================================= ==============================================

Helpers
-----------

========================================= ==============================================
luxon/helpers                             Various helper functions
luxon/helpers/db.py                       Database helper
luxon/helpers/jinja2.py                   Jinja2 helper
luxon/helpers/mail.py                     Luxon mail utility
luxon/helpers/policy.py                   Policy engine helper
luxon/helpers/rd.py                       Redis helper
========================================= ==============================================

Resources
------------

========================================= ==============================================
luxon/resources                           Resources provided by Luxon
luxon/resources/script/help.py            Command line **help**
luxon/resources/wsgi/index.py             API index         
========================================= ==============================================

Structures
-------------

========================================= ==============================================
luxon/structs                             Luxon Data Structures 
luxon/structs/models                      Luxon model classes
luxon/structs/cidict.py                   Case insensitice dictionary
luxon/structs/container.py                Property dictionary
luxon/structs/htmldoc.py                  HTMLDoc Object
luxon/structs/threaddict.py               Dictionary for threads
luxon/structs/threadlist.py               List for threads
========================================= ==============================================

Testing
------------

========================================= ==============================================
luxon/testing/wsgi                        Stubs for internal testing the WSGI interface
========================================= ==============================================

Utilities
-----------

========================================= ==============================================
luxon/utils                               All and sundry Luxon utilities 
========================================= ==============================================

Ancillary code
-------------------

========================================= ==============================================
luxon/constants.py                        Predefined constants usesd by Luxon
luxon/exceptions.py                       Custom raisable exceptions
luxon/main.py                             Main entrypoint to Luxon
luxon/metadata.py                         Luxon metadata
luxon/wsgi.py                             WSGI launcher
========================================= ==============================================












































