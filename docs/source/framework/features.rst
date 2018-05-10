.. _features:

Features
========

Core Application features
    * Detect location of application root, can also be specified as argument.
    * config (All applications get access to 'settings.ini' with a object wrapped around configparser. It automatically loads config files and appends default configuration for the application environment)
    * Logger (Wrapper around python logging, that consumes the logging environment, it provides enhanced functionality like appending request context specific items to logs. Its configurable via 'settings.ini' globally and on a per module basis. This allows different logging handlers and levels per module)
    * Templating (Jinja2 template engine exposed using our own Luxon Template Loader. This allows you to access templates in the form of package_name/template.html for example. However it also checks whether there is an overriding template for the application in its root the users can provide)
    * Router. (Fast modified router to route any path from example a URI based on method. It uses compiled router from Falcon project. This code is licensed as per Apache 2.0 License Copyright 2012-2017 by Rackspace Hosting, Inc. and other contributors, as noted in the individual source code files)
    * Policy Engine. (Fast rule-set based policy engine to validate rule sets defined in a 'policy.json'. This is used to provide customizable RBAC. Rules are compiled into python code for validation)
    * Base Application, Request and Response classes.
    * Global (Configuration, App Object, Router, Current Request is all accessible via global known as 'g' preserving context)
    * Middleware. (Register Pre request, after routing before resource and post request methods from classes)
    * HTML. (Generate HTML Menus and content)
    * MetaClasses - (Classes that create singletons, per thread singletons, named singletons etc.)
    * DB API - Python PEP DB-API 2 complaint interface for SQLLite3 and MySQL/MariaDB.

Structs
    * Container (Case Insensitive hash table providing dict and object interface, it preserves the case stored for keys)
    * ThreadDict (Dictionary that only has key value pairs for the current thread)
    * ThreadList (List that only has key value pairs for the current thread)
    * CiDict (Simple case insensitive key dictionary)
    * HTMLDoc (HTML Document parser and creation - Provides minimal validation)
    * Models (ORM with field validation and integration to Luxon DB API)

Helpers
    * db (Provide Connection for database as per settings.ini)
    * render_template (Find and Render template in oneline)
    * redis (Return strict redis connection based on settings.ini configuration)

Utilities
    * cast (Cast objects safely to other types)
    * constants (Create constants in module, that are immutable. They can be nested str, bytes, dicts, tuples or lists).
    * encoding (Convert unicode to bytes and vice versa, detect binary, validate ascii and other comparisons)
    * files (Cached IO Wrapper for file objects, Track file changes and validators like is_socket)
    * filter (Filter functions such as filter_none_text)
    * formatting (Formatters such as format_ms(ms) that returns e.g. 10.5ms or days, hours etc.
    * global_counter (Counter for keeping order of anything instantiated)
    * js (JSON Dumps and Loads Wrapper. Provides bytes, datetime etc. support)
    * middleware (Funky decorator to wrap views in. So you create views that wraps others without using global middleware)
    * objects (Functions that provide object absolute names, and decorator that creates properties for dict values inside a class)
    * password (Functions to hash and validate passwords. e.g. BLOWFISH, SHA256, SHA512 etc.)
    * pool (Create a pool of any classes/objects)
    * split (Functions that split text into lines based on characters etc)
    * strings (Unquote String, indent a string, try_lower(attempt to lowercase) etc)
    * timer (Context timer returns actual processing time of code within the context block)
    * timezone (Timezone senstitive datetime functions and parsers)
    * unique (Generate random ids etc)
    * uri (Parse URI Strings defined in IETF RFC 3986 for example parse_qs, host_from_uri etc)
