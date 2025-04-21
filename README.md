# 📇 Contacts API – FastAPI + SQLAlchemy + PostgreSQL + Redis

## 📝 Project Overview

This project is a RESTful API for storing and managing contacts. It is built using **FastAPI** and uses **SQLAlchemy** as the ORM layer to interact with a **PostgreSQL** database. The API implements **Redis** caching for improved performance.

The API allows users to perform basic CRUD operations on contact records, as well as search contacts and retrieve upcoming birthdays.

---

## 🚀 Features

- Create a new contact
- Retrieve all contacts
- Retrieve a single contact by ID
- Update an existing contact
- Delete a contact
- Search contacts by first name, last name, or email
- Retrieve contacts with birthdays in the next 7 days
- Response caching with Redis
- Fully documented with Swagger/OpenAPI

---

## 🛠 Tech Stack

- **FastAPI** – for building the web API
- **SQLAlchemy** – ORM for database interactions
- **Pydantic** – for data validation and serialization
- **PostgreSQL** – database engine
- **Redis** – for response caching
- **Uvicorn** – ASGI server for running the FastAPI app

---

