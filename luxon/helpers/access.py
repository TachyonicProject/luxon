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

from luxon.exceptions import AccessDeniedError

def validate_access(req, obj_dict):
    if ('domain' in obj_dict and
            req.credentials.domain and
            req.credentials.domain != obj_dict['domain']):
        raise AccessDeniedError('object not in context domain "%s"' %
				  req.credentials.domain)

    if ('tenant_id' in obj_dict and
            req.credentials.tenant_id and
            (req.credentials.tenant_id != obj_dict['tenant_id'] and
             req.credentials.tenant_id != obj_dict['id'])):
        raise AccessDeniedError('object not in context tenant "%s"' %
                                req.credentials.tenant_id)

    return True


def validate_set_scope(req, obj_dict):
    if 'domain' in obj_dict:
        if (req.credentials.domain == req.context_domain or
                req.credentials.domain is None):
            if obj_dict['domain'] is None:
                if req.context_domain is not None:
                    obj_dict.update({"domain": req.context_domain})
        else:
            raise AccessDeniedError(
                "Token not scoped for domain '%s'" % req.context_domain)

    if 'tenant_id' in obj_dict:
        if (req.credentials.tenant_id == req.context_tenant_id or
                req.credentials.tenant_id is None):
            if obj_dict['tenant_id'] is None:
                if req.context_tenant_id is not None:
                    obj_dict.update({"tenant_id": req.context_tenant_id})
        else:
            raise AccessDeniedError(
                "Token not scoped for Tenant '%s'" % req.context_tenant_id)
