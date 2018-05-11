# -*- coding: utf-8 -*-
# Copyright (c) 2018 Christiaan Frans Rademan.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holders nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF
# THE POSSIBILITY OF SUCH DAMAGE.
import os
import site
import multiprocessing


def server(app_root=None, ip='127.0.0.1', port='8000'):
    try:
        import gunicorn.app.base
        from gunicorn.six import iteritems
    except ImportError:
        print("Requires Gunicorn - pip install gunicorn")
        exit()

    def number_of_workers():
        return (multiprocessing.cpu_count() * 4) + 1

    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super(StandaloneApplication, self).__init__()

        def load_config(self):
            config = dict([(key, value)
                           for key, value in iteritems(self.options)
                           if key in self.cfg.settings and value is not None])
            for key, value in iteritems(config):
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application

    print('Loading Application %s' % app_root)

    options = {
        'bind': '%s:%s' % (ip, port),
        'workers': number_of_workers(),
        'capture_output': True
    }
    app_root = os.path.abspath(app_root)
    site.addsitedir(os.path.join(os.getcwd(), '../'))

    os.chdir(app_root)
    if not os.path.isfile(app_root.rstrip('/') + '/wsgi.py'):
        raise FileNotFoundError(app_root.rstrip('/') + '/wsgi.py')

    with open(app_root.rstrip('/') + '/wsgi.py', 'r') as wsgi_file:
        exec_g = {}
        exec(wsgi_file.read(), exec_g, exec_g)

    import luxon.core.servers.web.static

    while True:
        StandaloneApplication(exec_g['application'], options).run()
