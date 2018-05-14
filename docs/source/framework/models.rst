.. _models:

Models - ORM
============
A model is the data structure of information. It contains the fields, types and restrictions of the data you’re storing. A model can map to a single database table.

The basics:

    * Each model is a Python class that subclasses luxon.models or luxon.model
    * luxon.model is for a single object with fields.
    * luxon.models contains list/rows of objects with fields.
    * Using models optionally gives you conveniantly maintained and generated database.

The **luxon** command line tool provides an option **luxon -d** to create or update database schema. However it requires the application root to have a correctly configured *settings.ini* with relevant database configuration.

Warning:
	Please backup your database before updating the schema.

While working with 'models' object you can iterate, update rows and so forth. It behaves a like a list data structure with 'model' objects that behave like a dictionary of columns/fields. The rollback and commit can be used without database. 

Using models with database require you to define Primary Key using 'primary_key' class attribute. Its a reference to relevant field.

Note:
	To use a model with database you will need to decorate it with **luxon.database**
	'Integer' type fields as *primary_key* will automatically increment. However auto increment 		is only relevant when using database.

Example
-------
.. code:: python

	from uuid import uuid4

	from luxon import database_model
	from luxon import Models
	from luxon import Uuid
	from luxon import String
	from luxon import Text
	from luxon import DateTime
	from luxon import Boolean
	from luxon import Email
	from luxon import Phone
	from luxon import Enum
	from luxon import Index
	from luxon import ForeignKey
	from luxon import UniqueIndex
	from luxon.utils.timezone import now

	ROLES = [
		('00000000-0000-0000-0000-000000000000', 'Root', None, now()),
		(str(uuid4()), 'Operations', None, '0000-00-00 00:00:00'),
		(str(uuid4()), 'Administrator', None, '0000-00-00 00:00:00'),
		(str(uuid4()), 'Account Manager', None, '0000-00-00 00:00:00'),
		(str(uuid4()), 'Billing', None, '0000-00-00 00:00:00'),
		(str(uuid4()), 'Customer', None, '0000-00-00 00:00:00'),
		(str(uuid4()), 'Support', None, '0000-00-00 00:00:00'),
	]

	@database_model()
	class role(Models):
		id = Uuid(default=uuid4)
		name = String(max_length=64)
		description = Text()
		creation_time = DateTime(default=now)
		primary_key = id
		unique_role = UniqueIndex(name)
		db_default_rows = ROLES
		roles = Index(name)


	DOMAINS = [
		('00000000-0000-0000-0000-000000000000', 'default', None, 1, now()),
	]

	@database_model()
	class domain(Models):
		id = Uuid(default=uuid4)
		name = String(max_length=64)
		description = Text()
		enabled = Boolean(default=True)
		creation_time = DateTime(default=now)
		primary_key = id
		unique_domain = UniqueIndex(name)
		db_default_rows = DOMAINS
		domains = Index(name)

	@database_model()
	class tenant(Models):
		id = Uuid(default=uuid4)
		domain_id = Uuid()
		tenant_id = Uuid()
		name = String(max_length=100)
		enabled = Boolean(default=True)
		creation_time = DateTime(default=now)
		unique_tenant = UniqueIndex(domain_id, name)
		tenants = Index(id, domain_id)
		tenants_search_name = Index(domain_id, name)
		tenants_per_domain = Index(domain_id)
		primary_key = id


	USERS = [
		('00000000-0000-0000-0000-000000000000', 'tachyonic',
		 '00000000-0000-0000-0000-000000000000', None,
		 'root', '$2b$12$QaWa.Q3gZuafYXkPo3EJRuSJ1wGuutShb73RuH1gdUVri82CU6V5q',
		 None, 'Default Root User', None, None, None, '0000-00-00 00:00:00',
		 1, now()),
	]

	@database_model()
	class user(Models):
		id = Uuid(default=uuid4)
		tag = String(max_length=30)
		domain_id = Uuid()
		tenant_id = Uuid()
		username = String(max_length=100)
		password = String(max_length=100)
		email = Email(max_length=255)
		name = String(max_length=100)
		phone_mobile = Phone()
		phone_office = Phone()
		designation = Enum('Mr','Mrs','Dr', 'Ms')
		last_login = DateTime()
		enabled = Boolean(default=True)
		creation_time = DateTime(default=now)
		unique_username = UniqueIndex(domain_id, username)
		user_tenant_ref = ForeignKey(tenant_id, tenant.id)
		user_domain_ref = ForeignKey(domain_id, domain.id)
		users = Index(domain_id, username)
		users_tenants = Index(domain_id, tenant_id)
		users_domain = Index(domain_id)
		primary_key = id
		db_default_rows = USERS


	USER_ROLES = [
		('00000000-0000-0000-0000-000000000000',
		 '00000000-0000-0000-0000-000000000000',
		 '00000000-0000-0000-0000-000000000000',
		 None,
		 '00000000-0000-0000-0000-000000000000',
		 now()),
	]

	@database_model()
	class user_role(Models):
		id = Uuid(default=uuid4)
		role_id = Uuid()
		domain_id = Uuid()
		tenant_id = Uuid()
		user_id = Uuid()
		creation_time = DateTime(default=now)
		unique_user_role = UniqueIndex(role_id, tenant_id, user_id)
		user_role_id_ref = ForeignKey(role_id, role.id)
		user_role_domain_ref = ForeignKey(domain_id, domain.id)
		user_role_tenant_id_ref = ForeignKey(tenant_id, tenant.id)
		user_role_user_id_ref = ForeignKey(user_id, user.id)
		primary_key = id
		db_default_rows = USER_ROLES
..
	Models Class
	------------
	.. autoclass:: luxon.Models
	    :members:


Model Class
-----------

.. autoclass:: luxon.Model
    :members:

Fields
------

**Conveniantly accessible using 'from luxon import fields'**

.. autoclass:: luxon.String
    :members:
    :inherited-members:

.. autoclass:: luxon.Integer
    :members:
    :inherited-members:

.. autoclass:: luxon.Float
    :members:
    :inherited-members:

.. autoclass:: luxon.Double
    :members:
    :inherited-members:

.. autoclass:: luxon.Decimal
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyInt
    :members:
    :inherited-members:

.. autoclass:: luxon.SmallInt
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumInt
    :members:
    :inherited-members:

.. autoclass:: luxon.BigInt
    :members:
    :inherited-members:

.. autoclass:: luxon.DateTime
    :members:
    :inherited-members:

.. autoclass:: luxon.PyObject
    :members:
    :inherited-members:

.. autoclass:: luxon.Blob
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.LongBlob
    :members:
    :inherited-members:

.. autoclass:: luxon.Text
    :members:
    :inherited-members:

.. autoclass:: luxon.TinyText
    :members:
    :inherited-members:

.. autoclass:: luxon.MediumText
    :members:
    :inherited-members:

.. autoclass:: luxon.Enum
    :members:
    :inherited-members:

.. autoclass:: luxon.Boolean
    :members:
    :inherited-members:

.. autoclass:: luxon.Uuid
    :members:
    :inherited-members:

.. autoclass:: luxon.Index
    :members:
    :inherited-members:

.. autoclass:: luxon.UniqueIndex
    :members:
    :inherited-members:

.. autoclass:: luxon.ForeignKey
    :members:
    :inherited-members:

.. autoclass:: luxon.Email
    :members:
    :inherited-members:

.. autoclass:: luxon.Phone
    :members:
    :inherited-members:
