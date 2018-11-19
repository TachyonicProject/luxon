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
from luxon.utils import pyver
from luxon import metadata

# The big 'g' for accessing process wide globals.
from luxon.core.globals import luxon_globals as g

# Global Router
import luxon.core.router
router = luxon.core.router.Router()

# Registered Plugin Environment
import luxon.core.register
register = luxon.core.register.Register()

# Below is for conveniance.
from luxon.utils import js

from luxon.helpers.menu import Menu
from luxon.helpers.template import render_template
from luxon.helpers.rd import strict as redis
from luxon.helpers.db import db
from luxon.helpers.policy import policy
from luxon.helpers.sendmail import sendmail
from luxon.helpers.memoize import memoize
from luxon.helpers.rmq import rmq

from luxon.structs.models.model import Model
from luxon.structs.models.sqlmodel import SQLModel

from luxon.core.config import Config
from luxon.core.logger import GetLogger

__version__ = metadata.version
__author__ = metadata.author
__license__ = metadata.license
__copyright__ = metadata.copyright
__identity__ = metadata.identity
