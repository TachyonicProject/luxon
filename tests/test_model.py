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
from decimal import Decimal as PyDecimal

from luxon import register
from luxon import SQLModel
from luxon import g
from luxon.core.config.defaults import defaults
from luxon import db
from luxon.core.app import App

g.app_root = os.getcwd()
g.app = App("UnitTest", ini='/dev/null')
g.app.config.read_dict(defaults)
g.app.config['database'] = {}
g.app.config['database']['type'] = 'sqlite3'
g.app.config['database']['database'] = 'test.db'


@register.model()
class Model_Test2(SQLModel):
    id = SQLModel.Integer(length=11, null=True)
    primary_key = id
    stringcol = SQLModel.String(length=128)
    floatcol = SQLModel.Float(4,4)
    doublecol = SQLModel.Double(4,4)
    decimalcol = SQLModel.Decimal(4,4)
    datetimecol = SQLModel.DateTime(4,4)
    pyobject = SQLModel.PyObject()
    blob = SQLModel.Blob()
    text = SQLModel.Text()
    enum = SQLModel.Enum('option1', 'option2')
    boolean = SQLModel.Boolean()
    unique_index2 = SQLModel.UniqueIndex(stringcol)

@register.model()
class Model_Test1(SQLModel):
    id = SQLModel.Integer(length=11, null=True)
    primary_key = id
    stringcol = SQLModel.String(length=128)
    floatcol = SQLModel.Float(4,4)
    doublecol = SQLModel.Double(4,4)
    decimalcol = SQLModel.Decimal(4,4)
    datetimecol = SQLModel.DateTime(4,4)
    pyobject = SQLModel.PyObject()
    blob = SQLModel.Blob()
    text = SQLModel.Text()
    enum = SQLModel.Enum('option1', 'option2')
    boolean = SQLModel.Boolean()
    unique_index1 = SQLModel.UniqueIndex(stringcol)
    fk = SQLModel.ForeignKey((stringcol), (Model_Test2.stringcol))


def test_model():
    global test1, test2

    with db() as conn:
        try:
            conn.execute('DROP TABLE %s' % 'Model_Test1')
            conn.execute('DROP TABLE %s' % 'Model_Test2')
        except:
            pass

    test1 = Model_Test1()
    test2 = Model_Test2()
    test2.create_table()
    test1.create_table()
    new = {}
    new['stringcol'] = 'String Col'
    new['floatcol'] = 123.22
    new['doublecol'] = 123.22
    new['decimalcol'] = 123.22
    new['datetimecol'] = '1983-01-17 00:00:00'
    new['pyobject'] = {}
    new['blob'] = b'Binary Data'
    new['text'] = "string of text"
    new['enum'] = 'option1'
    new['boolean'] = True
    test2.update(new)
    test2.commit()
    new = {}
    new['stringcol'] = 'String Col'
    new['floatcol'] = 123.22
    new['doublecol'] = 123.22
    new['decimalcol'] = 123.22
    new['datetimecol'] = '1983-01-17 00:00:00'
    new['pyobject'] = {}
    new['blob'] = b'Binary Data'
    new['text'] = "string of text"
    new['enum'] = 'option1'
    new['boolean'] = True
    test1.update(new)
    test1.commit()
    assert isinstance(test1['pyobject'], dict)
    test1 = Model_Test1()
    test1.sql_query("SELECT * FROM Model_Test1")
    assert isinstance(test1['id'], int)
    assert isinstance(test1['floatcol'], float)
    assert isinstance(test1['doublecol'], float)
    assert isinstance(test1['decimalcol'], PyDecimal)
    assert isinstance(test1['blob'], bytes)
    assert isinstance(test1['text'], str)
    assert isinstance(test1['enum'], str)
    assert isinstance(test1['boolean'], bool)
