.. _structure:

Package Layout
==============

This table serves as an exact index of the Luxon source code.

Contributions
------------------------

========================================= ==============================================
luxon/contrib                             Contributed functionality for Luxon.
========================================= ==============================================

Luxon Core
--------------

========================================= ==============================================
luxon/core                                Core Modules.
luxon/core/cache			  Caching classes.
luxon/core/config                         Config parser.
luxon/core/db                             Database API(s).
luxon/core/handlers                       Application Handlers.
luxon/core/handlers/wsgi                  WSGI interface handlers.
luxon/core/handlers/cmd			  Command Line Handler.
luxon/core/policy                         Policy RBAC Rule-Set Engine.
luxon/core/servers                        Servers for running application.
luxon/core/session                        Session manager.
luxon/core/utils                          Internal core utilities.
luxon/core/app.py			  Application launch.
luxon/core/auth.py                        Token authentication.
luxon/core/globals.py                     Global 'g' class.
luxon/core/logger.py                      Logging service, for debugging etc...
luxon/core/regex.py                       Regex patterns.
luxon/core/register.py                    Class of views/registration functions.
luxon/core/router.py                      Router Interface.
luxon/core/template.py                    Wrapper for Jinja2 Template Environment.
========================================= ==============================================

External Code
----------------

========================================= ==============================================
luxon/ext/falcon                          Application Routing Engine.
========================================= ==============================================

Helpers / Utilities
--------------------

========================================= ==============================================
luxon/helpers                             Various helpers.
luxon/helpers/access.py			  API access validator helpers.
luxon/helpers/api.py			  API Request/Response helpers.
luxon/helpers/cache.py			  Caching helpers.
luxon/helpers/crypto.py                   Crypto helpers.
luxon/helpers/db.py                       Database helpers.
luxon/helpers/memoize.py		  Memoize helper.
luxon/helper/menu.py			  HTML Menu generator helper.
luxon/helpers/policy.py                   Policy engine helper.
luxon/helpers/rd.py                       Redis helper.
luxon/helpers/rmq.py                      RabbitMQ Helper.
luxon/helpers/sendmail.py                 Send Mail helper.
luxon/helpers/template.py		  Template helper.
luxon/utils                               All and sundry Luxon utilities.
========================================= ==============================================

Resources
------------

========================================= ==============================================
luxon/resources                           Resources provided by Luxon.
luxon/resources/wsgi/index.py             API index.
========================================= ==============================================

Structures
-------------

========================================= ==============================================
luxon/structs                             Luxon Data Structures.
luxon/structs/models                      Luxon model data structures.
luxon/structs/cidict.py                   Case insensitive dictionary.
luxon/structs/container.py                Dictionary-like Object.
luxon/structs/htmldoc.py                  HTMLDoc Object.
luxon/structs/threaddict.py               Dictionary for threads.
luxon/structs/threadlist.py               List for threads.
========================================= ==============================================

Testing
-------

========================================= ==============================================
luxon/testing/wsgi                        Stubs for internal testing the WSGI interface.
========================================= ==============================================

Ancillary code
--------------

========================================= ==============================================
luxon/constants.py                        Predefined constants used by Luxon.
luxon/exceptions.py                       Custom raisable exceptions.
luxon/main.py                             Main entrypoint to Luxon.
luxon/metadata.py                         Luxon metadata.
luxon/wsgi.py                             WSGI launcher example.
========================================= ==============================================


Tests
-----

========================================= ==============================================
luxon/tests                               Directory housing all Unit Tests.
========================================= ==============================================


