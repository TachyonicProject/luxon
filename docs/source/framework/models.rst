.. _models:

============
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

While working with a 'models' object you can iterate, update rows and so forth. It behaves a like a list data structure with 'model' objects that behave like a dictionary of columns/fields. The rollback and commit can be used without database. 

Using models with database require you to define Primary Key using 'primary_key' class attribute. Its a reference to relevant field.

Note:
	To use a model with database you will need to decorate it with **luxon.database**
	'Integer' type fields as *primary_key* will automatically increment. However auto increment 		is only relevant when using database.

Example
-------
.. code:: python


	from uuid import uuid4

	from luxon import register
	from luxon import SQLModel
	from luxon.utils.timezone import now
	
	-------------------------------------------------
	# Model for roles
	-------------------------------------------------

	ROLES = [
	    ('00000000-0000-0000-0000-000000000000', 'Root', None, now()),
	    (str(uuid4()), 'Operations', None, now()),
	    (str(uuid4()), 'Administrator', None, now()),
	    (str(uuid4()), 'Account Manager', None, now()),
	    (str(uuid4()), 'Billing', None, now()),
	    (str(uuid4()), 'Support', None, now()),
	    (str(uuid4()), 'Customer', None, now()),
	    (str(uuid4()), 'Wholesale', None, now()),
	    (str(uuid4()), 'Minion', None, now()),
	]

	@register.model()
	class luxon_role(SQLModel):
	    id = SQLModel.Uuid(default=uuid4, internal=True)
	    name = SQLModel.String(max_length=64, null=False)
	    description = SQLModel.Text()
	    creation_time = SQLModel.DateTime(default=now, readonly=True)
	    primary_key = id
	    unique_role = SQLModel.UniqueIndex(name)
	    db_default_rows = ROLES
	    roles = SQLModel.Index(name)

	-------------------------------------------------
	# Model for domains
	-------------------------------------------------

	DOMAINS = [
	    ('00000000-0000-0000-0000-000000000000', 'default', None, 1, now()),
	]

	@register.model()
	class luxon_domain(SQLModel):
	    id = SQLModel.Uuid(default=uuid4, internal=True)
	    name = SQLModel.Fqdn(null=False)
	    description = SQLModel.Text()
	    enabled = SQLModel.Boolean(default=True)
	    creation_time = SQLModel.DateTime(default=now, readonly=True)
	    primary_key = id
	    unique_domain = SQLModel.UniqueIndex(name)
	    db_default_rows = DOMAINS
	    domains = SQLModel.Index(name)

	-------------------------------------------------
	# Model for tennants 
	-------------------------------------------------

	@register.model()
	class luxon_tenant(SQLModel):
	    id = SQLModel.Uuid(default=uuid4, internal=True)
	    domain = SQLModel.Fqdn(internal=True)
	    tenant_id = SQLModel.Uuid(internal=True)
	    name = SQLModel.String(max_length=100, null=False)
	    enabled = SQLModel.Boolean(default=True)
	    creation_time = SQLModel.DateTime(default=now, readonly=True)
	    unique_tenant = SQLModel.UniqueIndex(domain, name)
	    tenants = SQLModel.Index(id, domain)
	    tenants_search_name = SQLModel.Index(domain, name)
	    tenants_per_domain = SQLModel.Index(domain)
	    primary_key = id
	    tenant_domain_ref = SQLModel.ForeignKey(domain, luxon_domain.name)
	    tenant_parent_ref = SQLModel.ForeignKey(tenant_id, id)

	----------------------------------------------------
	# Model for users
	----------------------------------------------------

	USERS = [
	    ('00000000-0000-0000-0000-000000000000', 'tachyonic',
	     None, None,
	     'root', '$2b$12$QaWa.Q3gZuafYXkPo3EJRuSJ1wGuutShb73RuH1gdUVri82CU6V5q',
	     None, 'Default Root User', None, None, None, None,
	     1, now()),
	]


	@register.model()
	class luxon_user(SQLModel):
	    id = SQLModel.Uuid(default=uuid4, internal=True)
	    tag = SQLModel.String(hidden=True, max_length=30, null=False)
	    domain = SQLModel.Fqdn(internal=True)
	    tenant_id = SQLModel.Uuid(internal=True)
	    username = SQLModel.Username(max_length=100, null=False)
	    password = SQLModel.String(max_length=100, null=True)
	    email = SQLModel.Email(max_length=255)
	    name = SQLModel.String(max_length=100)
	    phone_mobile = SQLModel.Phone()
	    phone_office = SQLModel.Phone()
	    designation = SQLModel.Enum('', 'Mr', 'Mrs', 'Ms', 'Dr', 'Prof')
	    last_login = SQLModel.DateTime(readonly=True)
	    enabled = SQLModel.Boolean(default=True)
	    creation_time = SQLModel.DateTime(default=now, readonly=True)
	    unique_username = SQLModel.UniqueIndex(domain, username)
	    user_tenant_ref = SQLModel.ForeignKey(tenant_id, luxon_tenant.id)
	    user_domain_ref = SQLModel.ForeignKey(domain, luxon_domain.name)
	    users = SQLModel.Index(domain, username)
	    users_tenants = SQLModel.Index(domain, tenant_id)
	    users_domain = SQLModel.Index(domain)
	    primary_key = id
	    db_default_rows = USERS

	----------------------------------------------------
	# Model for user roles
	----------------------------------------------------


	USER_ROLES = [
	    ('00000000-0000-0000-0000-000000000000',
	     '00000000-0000-0000-0000-000000000000',
	     None,
	     None,
	     '00000000-0000-0000-0000-000000000000',
	     now()),
	]

	@register.model()
	class luxon_user_role(SQLModel):
	    id = SQLModel.Uuid(default=uuid4, internal=True)
	    role_id = SQLModel.Uuid()
	    domain = SQLModel.Fqdn(internal=True)
	    tenant_id = SQLModel.String()
	    user_id = SQLModel.Uuid()
	    creation_time = SQLModel.DateTime(readonly=True, default=now)
	    unique_user_role = SQLModel.UniqueIndex(role_id, tenant_id, user_id)
	    user_role_id_ref = SQLModel.ForeignKey(role_id, luxon_role.id)
	    user_role_domain_ref = SQLModel.ForeignKey(domain, luxon_domain.name)
	    user_role_tenant_ref = SQLModel.ForeignKey(tenant_id, luxon_tenant.id)
	    user_roles = SQLModel.Index(domain, tenant_id)
	    primary_key = id
	    db_default_rows = USER_ROLES


Model base Class
==================

.. autoclass:: luxon.Model
    :members:

.. _model_fields:

model Fields
=============

Data types supported by Luxon models

**Conveniantly accessible using 'model_name.field_name'**

Base Fields
------------

.. automodule:: luxon.structs.models.fields.basefields
	:members:

Blob Fields
------------

.. automodule:: luxon.structs.models.fields.blobfields
	:members:

Int Fields
------------

.. automodule:: luxon.structs.models.fields.intfields
	:members:

Sql Fields
------------

.. automodule:: luxon.structs.models.fields.sqlfields
	:members:

Text Fields
------------

.. automodule:: luxon.structs.models.fields.textfields
	:members:


