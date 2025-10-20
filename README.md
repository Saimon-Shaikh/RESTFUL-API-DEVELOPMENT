# RESTFUL-API-DEVELOPMENT

*COMPANY NAME*: CODTECH IT SOLUTIONS PVT.LTD

*NAME*: SAIMON SHAIKH

*INTERN ID*: CT06DR437

*DOMAIN NAME*: SOFTWARE DEVELOPMENT

*DURATION*: 6 WEEKS

*MENTOR NAME*: NEELA SANTOSH

# 📚 Task 2: Library Management RESTful API (CODTECH IT SOLUTIONS Internship)

This repository contains the source code for a robust and persistent **RESTful API** built to manage a Library's book inventory. This project was developed as **Task 2** of the CODTECH IT SOLUTIONS Software Developer Internship program, demonstrating proficiency in backend development, database integration, and adherence to advanced REST architectural principles.

---

## Project Overview

The primary goal was to create a professional API that provides full **CRUD** (Create, Read, Update, Delete) functionality for a `Book` resource. The core requirement was moving beyond volatile in-memory storage to **persistent database management** using an Object-Relational Mapper (ORM).

### Key Features:

* **Persistence:** Uses **Flask-SQLAlchemy** and a local **SQLite** database (`library.db`) to ensure all data is saved across server restarts.
* **Full REST Compliance:** Implements all standard HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`) with correct status codes and **HATEOAS** (Location header on `201 Created`).
* **Advanced Querying:** Supports **Filtering** and **Pagination** on the list endpoint (`GET /api/books`) for scalable data retrieval.
* **Error Handling:** Implements global error handlers (400, 404, 500) and specific database integrity checks (e.g., duplicate ISBN).

---

## Technical Implementation

The site's technical foundation is centered on Python Flask and the separation of application and data concerns.

### Database Integration and Persistence

The API achieves data persistence via the following structure:

* **Model Definition:** The `Book` resource is defined as a Python class inheriting from `db.Model`, mapping object attributes directly to database columns (e.g., `db.Column(db.Integer, primary_key=True)`).
* **Data Access Layer:** All data interactions (finding, adding, updating, deleting) use **SQLAlchemy Session** methods, completely replacing traditional raw SQL and eliminating the temporary in-memory list.
* **Seeding:** Initial mock data is automatically added upon the first run of the application if the database is empty, ensuring a functional starting point for testing.

### Advanced RESTful Design

The implementation adheres to modern API standards, going beyond simple CRUD:

* **PUT vs. PATCH:**
    * **`PUT /api/books/<id>`** is strictly used for *full replacement* of the resource.
    * **`PATCH /api/books/<id>`** is used for *partial updates* of specific fields.
* **Query Capabilities:** The `GET /api/books` endpoint is highly flexible, allowing consumers to:
    * **Filter** by `author`, `title`, `isbn`, and `publication_year` using URL query parameters.
    * **Paginate** using `page` and `per_page` parameters to manage large data sets efficiently.
* **Security & Errors:** Global error handlers catch exceptions (including `IntegrityError` from the database), ensuring a consistent JSON error structure for all client failures.

### Technologies Used:

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Backend Framework** | Python / Flask | Routing, Request Handling, JSON Serialization |
| **Data Persistence** | Flask-SQLAlchemy | Object-Relational Mapping (ORM) and Database Abstraction |
| **Database** | SQLite | Lightweight, file-based relational database (`library.db`) |
| **API Client Tool** | Postman / Insomnia | Used for development and testing all CRUD endpoints |
| **Integration** | Flask-CORS | Enables cross-origin requests for front-end consumption |
```eof

This README is now ready for your Task 2 repository! It clearly explains your architecture and highlights your best work.

Are you ready to start setting up the WebSocket server and client for **Task 3: Real-Time Collaboration Tool**?
