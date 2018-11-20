Releases
########

1.0.0 = BETA Release
--------------------

   * Require RabbitMQ Helper / Utility testing.
   * Requires updated completed documentation.

1.1.0 = BETA Release
--------------------

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
