Releases
########

1.0.0 = BETA Release (2018/11/19)
---------------------------------

   * Require RabbitMQ Helper / Utility testing.
   * Requires updated completed documentation.

1.1.0 = BETA Release (2018/11/20)
---------------------------------

    * Added functionality for defining SCRIPT_NAME in settings.ini.
      Required by NGINX, Gunicorn setup for example when
      using same virtualhost for multiple applications.
      It also checks for (X-Script-Name) header that can be defined.

      NGINX example:

        .. code::

                location /photonic {
                        include proxy_params;
                        proxy_redirect off;
                        proxy_pass http://unix:/var/www/photonic/photonic.sock:/;
                        proxy_set_header X-Script-Name /photonic;
                }

      Settings.ini example:

         .. code::

                [application]
                script = /photonic


1.1.1 = BETA Release (2018/11/23)
---------------------------------

   * Allow models to ignore validation errors when loading from sql.
   * Model default value of integer 0 does not show on html bootstrap4 forms fixed.
   * Only use stable version of pika 0.12.0.
   * Fixed several issues relating unit tests.
     Passlib updated interfaces for utils/password.py.
     Fixed Cookie testing, when empty body is received we expect 204 status code.
   * RabbitMQ Interface utility / helper tested functional.

1.2.0 = BETA Release (2018/11/26)
---------------------------------

   * Added Docker utilities utils/dk.py
   * Updated pkg.py Module. 
     Added file method to return file like object.

1.2.1 = BETA Release (2018/11/27)
---------------------------------

   * Fixed minor unexpected behaviour when two host headers is received.

1.3.0 = BETA Release (2019/01/27)
---------------------------------

   * Added distribute and receiver methods high level interfaces for
     rabbitmq utilities.
   * setup.py removed cython support.
   * setup.py replaced imp with importlib.
   * update documentation README.rst

1.4.0 = BETA Release (2019/02/05)
---------------------------------

   * In progress Clean up code/documentation - https://github.com/TachyonicProject/luxon/issues/11
   * Crypto helper added.
   * Updated Copyright, and pep8 complaint code clean.

1.4.1 = BETA Release (2019/02/05)
---------------------------------

   * Added missing copyright notice updates for contributers.
   * Fixed bug in html select using list to set default/selected value.

