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
# * Neither the model_name of the copyright holders nor the model_names of its
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

from luxon.core.register import _models
from luxon.core.register import _sa_models
from luxon.structs.models.sqlmodel import SQLModel
from luxon.helpers.sql import sql
from logging import getLogger

from sqlalchemy.ext.declarative import declarative_base

log = getLogger(__name__)


def backup_tables(conn):
    """Makes a backup of a database

    Retrieves the models in use and returns the corresponding tables and
    their entries from the database

    Args:
        conn (connection object): connection object for the database

    Returns:
        Dictionary containing all tables in the database.
        Each entry is a list(rows) of sequences(elements in row)
        with the key being the table name
    """
    models = {}
    for Model in reversed(_models):
        if issubclass(Model, SQLModel):
            if conn.has_table(Model.model_name):
                crsr = conn.execute("SELECT * FROM %s" % Model.model_name)
                models[Model.model_name] = crsr.fetchall()
                conn.commit()
    return models


def drop_tables(conn):
    """Empties database

    Deletes all the tables in a database that correspond to models in use

    Args:
        conn (connection object): the database to be deleted
    """
    for Model in reversed(_models):
        if issubclass(Model, SQLModel):
            if conn.has_table(Model.model_name):
                conn.execute('DROP TABLE %s' % Model.model_name)


def create_tables():
    """Creates tables for all models in g.models
    """
    for Model in _models:
        if issubclass(Model, SQLModel):
            Model.create_table()

    session_maker = sql()
    session = session_maker()
    engine = session.get_bind()

    for Model in _sa_models:
        try:
            Model.__table__.create(engine, checkfirst=True)
        except Exception as err:
            log.critical(err)

def restore_tables(conn, backup):
    """Restores database from backup

    Args:
        conn (connection object): connection object of the database
        backup (dict): backup dictionary
    """
    for Model in _models:
        if issubclass(Model, SQLModel):
            if Model.model_name in backup:
                conn.insert(Model.model_name, backup[Model.model_name])
            else:
                conn.insert(Model.model_name, Model.db_default_rows)
