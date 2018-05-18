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
luxon/core/handlers/cmd			  Command Line Handler
luxon/core/handlers/minion		  Minion Handler
luxon/core/policy                         Policy RBAC Rule-Set Engine.
luxon/core/servers                        Luxon servers

luxon/core/app.py			  Application Launch
luxon/core/auth.py                        PKI Authentication
luxon/core/globals.py                     Global 'g' class.
luxon/core/logger.py                      Logging service, for debugging etc...
luxon/core/regex.py                       Regex patterns
luxon/core/register.py                    Class of views/registration functions     
luxon/core/router.py                      Router Interface    
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
luxon/helpers/cache.py			  Caching helper
luxon/helpers/db.py                       Database helper
luxon/helpers/memoize.py		  Memoize function
luxon/helper/menu.py			  Menu tool helper
luxon/helpers/policy.py                   Policy engine helper
luxon/helpers/rd.py                       Redis helper
luxon/helpers/sendmail.py                 Send Mail helper
luxon/helpers/template.py		  Redis template helper
luxon/helpers/theme.py			  Theme helper

========================================= ==============================================

Resources
------------

========================================= ==============================================
luxon/resources                           Resources provided by Luxon
luxon/resources/wsgi/index.py             API index         
========================================= ==============================================

Structures
-------------

========================================= ==============================================
luxon/structs                             Luxon Data Structures 
luxon/structs/models                      Luxon model data structures
luxon/structs/cidict.py                   Case insensitice dictionary
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












































