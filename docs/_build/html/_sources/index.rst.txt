Contact Management REST API Documentation
=========================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

Introduction
------------
This is a REST API service for managing contacts with user authentication, email verification,
and avatar management capabilities. The API is built with FastAPI and uses SQLAlchemy for 
database operations.

Core Features
-------------
* User authentication and authorization
* Contact management with CRUD operations
* Email verification system
* Avatar upload and management
* Birthday reminder functionality

API Reference
=============

Authentication Endpoints
------------------------
.. automodule:: src.api.auth
   :members:
   :undoc-members:
   :show-inheritance:

User Management
---------------
.. automodule:: src.api.users
   :members:
   :undoc-members:
   :show-inheritance:

Contact Management
------------------
.. automodule:: src.api.contacts
   :members:
   :undoc-members:
   :show-inheritance:

Utility Endpoints
-----------------
.. automodule:: src.api.utils
   :members:
   :undoc-members:
   :show-inheritance:

Internal Architecture
=====================

Service Layer
-------------

Authentication Service
~~~~~~~~~~~~~~~~~~~~~~
.. automodule:: src.services.auth
   :members:
   :undoc-members:
   :show-inheritance:

Contact Service
~~~~~~~~~~~~~~~
.. automodule:: src.services.contacts
   :members:
   :undoc-members:
   :show-inheritance:

User Service
~~~~~~~~~~~~~
.. automodule:: src.services.users
   :members:
   :undoc-members:
   :show-inheritance:

Email Service
~~~~~~~~~~~~~
.. automodule:: src.services.email
   :members:
   :undoc-members:
   :show-inheritance:

File Upload Service
~~~~~~~~~~~~~~~~~~~
.. automodule:: src.services.upload_file
   :members:
   :undoc-members:
   :show-inheritance:

Data Layer
----------

.. _orm_declarative_metadata:

SQLAlchemy ORM Declarative Metadata
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Database Models
~~~~~~~~~~~~~~~
.. automodule:: src.database.models
   :members:
   :undoc-members:
   :show-inheritance:

Data Schemas
~~~~~~~~~~~~~
.. automodule:: src.schemas
   :members:
   :undoc-members:
   :show-inheritance:

Database Connection
~~~~~~~~~~~~~~~~~~~
.. automodule:: src.database.db
   :members:
   :undoc-members:
   :show-inheritance:

Configuration
~~~~~~~~~~~~~
.. automodule:: src.conf.config
   :members:
   :undoc-members:
   :show-inheritance:

Repository Layer
----------------

Contact Repository
~~~~~~~~~~~~~~~~~~
.. automodule:: src.repository.contacts
   :members:
   :undoc-members:
   :show-inheritance:

User Repository
~~~~~~~~~~~~~~~
.. automodule:: src.repository.users
   :members:
   :undoc-members:
   :show-inheritance:

Indices and References
======================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

