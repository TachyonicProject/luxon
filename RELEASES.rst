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
