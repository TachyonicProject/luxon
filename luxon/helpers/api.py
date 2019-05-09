# -*- coding: utf-8 -*-
# Copyright (c) 2018-2019 Christiaan Frans Rademan.
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
from ipaddress import ip_address
from math import ceil
from luxon.utils.sort import Itemgetter
from luxon.helpers.access import validate_access, validate_set_scope

from luxon import g
from luxon import db
from luxon.utils.sql import (Select,
                             Field,
                             Value,
                             Group,
                             And,
                             Or,
                             get_field)
from luxon.utils.api import search_params, search_datetime
from luxon.utils.cast import to_list
from luxon import SQLModel
from luxon.core.regex import SQLFIELD_RE
from luxon.utils.text import split

from luxon import GetLogger

log = GetLogger(__name__)


def raw_list(req, data, limit=None, context=True, sql=False,
             callbacks=None, **kwargs):
    # Step 1 Build Pages
    if limit is None:
        limit = int(req.query_params.get('limit', 10))

    page = int(req.query_params.get('page', 1))
    if sql is True:
        start = 0
        end = limit
        rows = len(data) + ((page - 1) * limit)
    else:
        start = (page - 1) * limit
        end = start + limit
        rows = len(data)

    # Step 2 Build Data Payload
    result = []
    search_query = ''
    for row in data:
        if context is True:
            if ('domain' in row and
                    req.context_domain is not None):
                if row['domain'] != req.context_domain:
                    continue
            if ('tenant_id' in row and
                    req.context_tenant_id is not None):
                if row['tenant_id'] != req.context_tenant_id:
                    continue
        if sql is False and to_list(req.query_params.get('search')):
            for search_field, value in search_params(req):
                search_query += '&search=%s:%s' % (search_field, value,)
                try:
                    if isinstance(row, (str, bytes),):
                        row_search_field = str(row).lower()
                        row_field = row
                    else:
                        row_search_field = str(row[search_field]).lower()
                        row_field = row[search_field]

                    if not row_search_field.startswith(value.lower()):
                        continue
                    elif row_field:
                        result.append(row)
                        break
                except KeyError:
                    raise ValueError("Unknown field '%s' in search" %
                                     search_field)
        else:
            result.append(row)

    # Step 3 Sort though data
    sort = to_list(req.query_params.get('sort'))
    sort_query = ''
    for order in sort:
        sort_query = '&sort=%s' % order
        try:
            order_field, order_type = split(order, ':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field sort field value." +
                             " Expecting 'field:desc' or 'field:asc'")

        if len(data) > 0 and sql is False:
            order_type = order_type.lower()
            # Check if field to order by is valid.
            if order_field not in data[0]:
                raise ValueError("Unknown field '%s' in sort" %
                                 order_field)

            # Sort field desc/asc
            if order_type == 'desc':
                try:
                    result = list(sorted(result,
                                         key=Itemgetter(order_field),
                                         reverse=True))
                except TypeError as e:
                    log.error(e)

            elif order_type == 'asc':
                try:
                    result = list(sorted(result,
                                         key=Itemgetter(order_field)))
                except TypeError as e:
                    log.error(e)
            else:
                raise ValueError('Bad order for sort provided')

    # Step 4 Limit rows based on pages.
    if limit > 0:
        if len(result) > limit:
            result = result[start:end]

    # Step 5 Parse callback on fields
    if callbacks:
        for row in result:
            for callback in callbacks:
                updates = {}
                for column in row:
                    if column == callback:
                        if row[column] is not None:
                            value = callbacks[callback](row[column])
                            if isinstance(value, dict):
                                updates.update(value)
                            else:
                                updates[callback] = value
                row.update(updates)

    # Step 6 Build links next &/ /previous
    links = {}
    if g.app.config.get('application', 'use_forwarded') is True:
        resource = (req.forwarded_scheme + "://" +
                    req.forwarded_host +
                    req.app + req.route)
    else:
        resource = (req.scheme + "://" +
                    req.netloc +
                    req.app + req.route)

    if limit > 0:
        if page > 1:
            links['previous'] = resource + '?limit=%s&page=%s' % (limit, page,)
            links['previous'] += sort_query
            links['previous'] += search_query

        if page < ceil(rows / limit):
            links['next'] = resource + '?limit=%s&page=%s' % (limit, page + 2,)
            links['next'] += sort_query
            links['next'] += search_query
        pages = ceil(rows / limit)
    else:
        pages = 1

    # Step 7 Finally return result
    return {
        'links': links,
        'payload': result,
        'metadata': {
            "records": rows,
            "page": page,
            "pages": pages,
            "per_page": limit,
            "sort": sort,
            "search": to_list(req.query_params.get('search')),
        }
    }


def sql_list(req, select, fields={}, limit=None, order=True,
             search=None, callbacks=None, context=True):

    if not isinstance(select, Select):
        select = Select(select)

    # Step 1 Build Fields
    for field in fields:
        select.fields = Field(field)

    # Step 2 Build sort
    if order:
        order_fields = {}
        if isinstance(order, list):
            for field in order:
                field, as_field = get_field(field)
                if as_field:
                    order_fields[as_field] = field
                else:
                    order_fields[field] = field

        sort = to_list(req.query_params.get('sort'))
        if len(sort) > 0:
            for order in sort:
                try:
                    order_field, order_type = split(order, ':')
                except (TypeError, ValueError):
                    raise ValueError("Invalid field sort field value." +
                                     " Expecting 'field:desc' or 'field:asc'")

                if order_fields and order_field in order_fields:
                    order_field = order_fields[order_field]
                elif order_fields:
                    raise ValueError("Field '%s' not sortable" %
                                     order_field)

                order_type = order_type.lower()
                if not SQLFIELD_RE.match(order_field):
                    raise ValueError("Invalid field '%s' in sort" %
                                     order_field)
                if order_type == "asc":
                    order_type = "<"
                elif order_type == "desc":
                    order_type = ">"
                else:
                    raise ValueError('Bad order for sort provided')
                select.order_by = Field(order_field)(order_type)

    # Step 3 Build Pages
    if limit is None:
        limit = int(req.query_params.get('limit', 10))

    page = int(req.query_params.get('page', 1)) - 1
    start = page * limit

    if limit > 0:
        select.limit(start, limit + 100)

    # Step 4 Search
    searches = to_list(req.query_params.get('search'))
    conditions = []
    search_parsed = {}
    if isinstance(search, dict):
        for field in search:
            if '.' in field:
                search_parsed[field.split('.')[1]] = (field,
                                                      search[field],)
            else:
                search_parsed[field] = (field,
                                        search[field],)

    for search_req in searches:
        try:
            search_field, search_value = split(search_req, ':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field search field value." +
                             " Expecting 'field:value'")
        if not SQLFIELD_RE.match(search_field):
            raise ValueError("Unknown field format '%s' in search" %
                             search_field)

        if isinstance(search, dict):
            if search_field in search_parsed:
                if isinstance(search_parsed[search_field][1], str):
                    if search_parsed[search_field][1] == 'datetime':
                        search_value = search_datetime(search_value)
                        if search_value[0] is not None:
                            if search_value[1] is True:
                                conditions.append(
                                    Field(
                                        search_parsed[search_field][0])
                                    >= Value(search_value[0]))
                            else:
                                conditions.append(
                                    Field(
                                        search_parsed[search_field][0])
                                    == Value(search_value[0]))
                    elif search_parsed[search_field][1] == 'ip':
                        try:
                            search_value = ip_address(search_value).packed
                            conditions.append(
                                Field(
                                    search_parsed[search_field][0])
                                == Value(search_value))
                        except ValueError:
                            pass
                    else:
                        raise ValueError("Unknown search field type '%s'" %
                                         search_field)
                elif issubclass(search_parsed[search_field][1], str):
                    conditions.append(
                        Field(
                            search_parsed[search_field][0])
                        ^ Value(search_value))
                elif issubclass(search_parsed[search_field][1], int):
                    try:
                        search_value = int(search_value)
                    except ValueError:
                        raise ValueError("Expecting integer for search" +
                                         " field '%s'" % search_field)
                    conditions.append(
                        Field(
                            search_parsed[search_field][0])
                        == Value(search_value))
                elif issubclass(search_parsed[search_field][1], bytes):
                    conditions.append(
                        Field(
                            search_parsed[search_field][0])
                        == Value(search_value))
                else:
                    raise ValueError("Unknown search field type '%s'" %
                                     search_field)
            else:
                raise ValueError("Unknown field '%s' in search" %
                                 search_field)

        else:
            raise ValueError("Search not availible")

    if conditions:
        select.where = Group(Or(*conditions))

    # Step 5 Query
    with db() as conn:
        if context:
            grouped = []
            if isinstance(context, bool):
                context = select._table

            if (conn.has_field(context, 'domain') and
                    req.context_domain is not None):
                grouped.append(Field(
                    '%s.domain' % context) == Value(req.context_domain))

            if (conn.has_field(context, 'tenant_id') and
                    req.context_tenant_id is not None):
                grouped.append(Field(
                    '%s.tenant_id' % context) == Value(
                        req.context_tenant_id))

            if grouped:
                    select.where = Group(And(*grouped))

        result = conn.execute(select.query, select.values).fetchall()

    # Step 6 we pass it to standard list output provider
    return raw_list(req, result, limit=limit, sql=True, callbacks=callbacks)


def obj(req, ModelClass, sql_id=None, hide=None):
    if not issubclass(ModelClass, SQLModel):
        raise ValueError('Expecting SQL Model')

    model = ModelClass(hide=hide)

    if sql_id:
        model.sql_id(sql_id)

        validate_access(req, model)

    if req.method in ['POST', 'PATCH', 'PUT']:
        model.update(req.json)
        validate_set_scope(req, model)
    elif (req.method == 'DELETE' and
            issubclass(ModelClass, SQLModel) and
            sql_id):
        model.delete()

    return model
