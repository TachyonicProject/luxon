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
from math import ceil
from luxon.utils.sort import Itemgetter
from luxon.helpers.access import validate_access, validate_set_scope

from luxon import g
from luxon import db
from luxon.utils.sql import build_where, build_like
from luxon.utils.cast import to_list
from luxon import SQLModel
from luxon.exceptions import AccessDeniedError

from luxon import GetLogger

log = GetLogger(__name__)

def search_params(req):
    searches = to_list(req.query_params.get('search'))
    for search in searches:
        try:
            search_field, value = search.split(':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field search field value." +
                             " Expecting 'field:value'")

        yield (search_field, value,)

def raw_list(req, data, limit=None, context=True, sql=False):
    # Step 1 Build Pages
    if limit is None:
        limit = int(req.query_params.get('limit', 10))

    page = int(req.query_params.get('page', 1)) - 1
    if sql is True:
        start = 0
        end = limit
        rows = len(data) + (page * limit)
    else:
        start = page * limit
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
            order_field, order_type = order.split(':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field sort field value." +
                             " Expecting 'field:desc' or 'field:asc'")

        if len(data) > 0:
            order_type = order_type.lower()
            # Check if field to order by is valid.
            if order_field not in data[0]:
                raise ValueError("Unknown field '%s' in sort" %
                                 order_field)

            # Sort field desc/asc
            if order_type == 'desc':
                result = list(sorted(result, key=Itemgetter(order_field),
                                     reverse=True))
            elif order_type == 'asc':
                result = list(sorted(result, key=Itemgetter(order_field)))
            else:
                raise ValueError('Bad order for sort provided')

    # Step 4 Limit rows based on pages.
    if limit > 0:
        if len(result) > limit:
            result = result[start:end]

    # Step 5 Build links next &/ /previous
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
        if page + 1 > 1:
            links['previous'] = resource + '?limit=%s&page=%s' % (limit, page,)
            links['previous'] += sort_query
            links['previous'] += search_query

        if page + 1 < ceil(rows / limit):
            links['next'] = resource + '?limit=%s&page=%s' % (limit, page + 2,)
            links['next'] += sort_query
            links['next'] += search_query
        pages = ceil(rows / limit)
    else:
        pages = 1

    # Step 6 Finally return result
    return {
        'links': links,
        'payload': result,
        'metadata': {
            "records": rows,
            "page": page + 1,
            "pages": pages,
            "per_page": limit,
            "sort": sort,
            "search": to_list(req.query_params.get('search')),
        }
    }


def sql_list(req, table, sql_fields, limit=None, group_by=None, where=None,
             ordering=True,  **kwargs):
    #  Build Fields, support fields as in tuple/list
    fields = {}
    count_field = None
    for field in sql_fields:
        if isinstance(field,  (tuple, list,)):
            fields[field[1]] = field[0]
            if count_field is None:
                count_field = field[0]
        else:
            fields[field] = field
            if count_field is None:
                count_field = field

    # Step 1 Build sort
    sort_range_query = None
    if ordering:
        sort = to_list(req.query_params.get('sort'))
        if len(sort) > 0:
            ordering = []
            for order in sort:
                try:
                    order_field, order_type = order.split(':')
                except (TypeError, ValueError):
                    raise ValueError("Invalid field sort field value." +
                                     " Expecting 'field:desc' or 'field:asc'")
                order_type = order_type.lower()
                if order_type != "asc" and order_type != "desc":
                    raise ValueError('Bad order for sort provided')
                if order_field not in fields:
                    raise ValueError("Unknown field '%s' in sort" %
                                     order_field)
                order_field = fields[order_field]
                ordering.append("%s %s" % (order_field, order_type))

            sort_range_query = " ORDER BY %s" % ','.join(ordering)

    # Step 2 Build Pages
    if limit is None:
        limit = int(req.query_params.get('limit', 10))

    page = int(req.query_params.get('page', 1)) - 1
    start = page * limit

    if limit <= 0:
        limit_range_query = ""
    else:
        limit_range_query = " LIMIT %s, %s" % (start, limit * 2,)

    # Step 3 Search
    search_query = {}
    searches = to_list(req.query_params.get('search'))
    for search in searches:
        try:
            search_field, value = search.split(':')
        except (TypeError, ValueError):
            raise ValueError("Invalid field search field value." +
                             " Expecting 'field:value'")
        if search_field not in fields:
            raise ValueError("Unknown field '%s' in search" %
                             search_field)
        search_query[fields[search_field]] = value

    # Step 4 Prepre to run queries
    #fields_str = ", ".join(fields.values())
    fields_str = None
    for field in fields:
        if fields_str is None:
            fields_str = "%s as %s" % (fields[field], field)
        else:
            fields_str += ", %s as %s" % (fields[field], field)

    context_query = {}
    context_query.update(kwargs)
    if where:
        context_query.update(where)

    with db() as conn:
        # Check if Table is actual table or joins...
        # If joined, view is expected to add where clause for validation..
        if " " not in table:
            if (conn.has_field(table, 'domain') and
                    req.context_domain is not None):
                context_query['domain'] = req.context_domain

            if (conn.has_field(table, 'tenant_id') and
                    req.context_tenant_id is not None):
                context_query['tenant_id'] = req.context_tenant_id

        where, values = build_where(**context_query)
        search_where, search_values = build_like(**search_query,
                                                 operator='OR')

        # Step 6 we get the data
        sql = 'SELECT %s FROM %s' % (fields_str, table,)

        if where or search_where:
            sql += " WHERE "

        if where:
            sql += " " + where

        if where and search_where:
            sql += " AND "

        if search_where:
            sql += " " + search_where

        if group_by:
            sql += " GROUP BY " + group_by

        if sort_range_query:
            sql += sort_range_query

        sql += limit_range_query



        result = conn.execute(sql,
                              values + search_values).fetchall()

    # Step 7 we pass it to standard list output provider
    return raw_list(req, result, limit=limit, sql=True)


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
