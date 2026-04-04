# Contact Manager System

A full-stack contact management web application built with **Django** (backend REST API) and a **vanilla JS single-page frontend**. Users can register, log in, and manage their personal contacts with support for search, CSV/JSON export, and account lockout protection.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation & Setup](#installation--setup)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [API Reference](#api-reference)
- [Data Validation Rules](#data-validation-rules)
- [Security Notes](#security-notes)
- [License](#license)

---

## Features

- **User Authentication** — Register and log in with session-based auth (2-hour session expiry)
- **Account Lockout** — Locks account for 60 seconds after 3 failed login attempts
- **Contact CRUD** — Create, read, update, and delete contacts per user
- **Search** — Search contacts by name, phone, email, or all fields at once
- **Export** — Download your contacts as CSV or JSON
- **Input Validation** — Server-side validation for all fields (name, phone, email, username, password)
- **Single-Page App** — Frontend served as a single `index.html` with no page reloads

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3, Django 4.2              |
| Database  | MySQL (via `mysqlclient`)         |
| Frontend  | Vanilla HTML/CSS/JavaScript (SPA) |
| Sessions  | Django session framework (DB-backed) |

---

## Project Structure

```
contact-manager-System-main/
├── contact_manager/          # Django project config
│   ├── settings.py           # Settings (DB, middleware, sessions)
│   ├── urls.py               # Root URL routing
│   ├── wsgi.py               # WSGI entry point
│   └── db_utils.py           # Auto-creates MySQL DB if missing
│
├── contacts/                 # Main Django app
│   ├── models.py             # AppUser and Contact models
│   ├── views.py              # All API views (auth + contacts + export)
│   ├── urls.py               # API URL patterns under /api/
│   ├── validators.py         # Input validation logic
│   └── migrations/           # Database migrations
│
├── templates/
│   └── index.html            # Single-page frontend (HTML + CSS + JS)
│
├── manage.py                 # Django management CLI
├── requirements.txt          # Python dependencies
└── LICENSE
```

---

## Prerequisites

- Python 3.9+
- MySQL 5.7+ or 8.0+
- pip

---

## Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/contact-manager-System.git
cd contact-manager-System
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

> **If `mysqlclient` fails to install** (common on some systems), install `PyMySQL` instead:
> ```bash
> pip install PyMySQL
> ```
> Then add these two lines at the top of `contact_manager/settings.py`:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

### 4. Set Up the Database

Make sure your MySQL server is running. The app will automatically create the database (`contact_manager_db`) if it doesn't exist, thanks to `db_utils.py`.

Alternatively, create it manually:

```sql
CREATE DATABASE contact_manager_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 5. Apply Migrations

```bash
python manage.py migrate
```

---

## Configuration

Database credentials and other settings are read from environment variables. You can set them in your shell or use a `.env` file with a tool like `python-dotenv`.

| Environment Variable | Default              | Description              |
|----------------------|----------------------|--------------------------|
| `DB_NAME`            | `contact_manager_db` | MySQL database name      |
| `DB_USER`            | `root`               | MySQL username           |
| `DB_PASSWORD`        | `system`             | MySQL password           |
| `DB_HOST`            | `localhost`          | MySQL host               |
| `DB_PORT`            | `3306`               | MySQL port               |

**Example — setting variables in the shell:**

```bash
export DB_USER=myuser
export DB_PASSWORD=mypassword
```

> ⚠️ **Production:** Change the `SECRET_KEY` in `settings.py` and set `DEBUG = False`. Never commit credentials to version control.

---

## Running the Application

```bash
python manage.py runserver
```

Then open your browser at **http://127.0.0.1:8000/**

The frontend SPA is served at `/` and all API endpoints are available under `/api/`.

---

## API Reference

All request and response bodies use JSON. Authentication is session-based; the session cookie is set automatically on login.

### Authentication

| Method | Endpoint         | Description                         |
|--------|------------------|-------------------------------------|
| POST   | `/api/register`  | Create a new account                |
| POST   | `/api/login`     | Log in and start a session          |
| POST   | `/api/logout`    | End the current session             |
| GET    | `/api/me`        | Get the currently logged-in user    |

**Register — request body:**
```json
{ "username": "alice", "password": "secret123" }
```

**Login — request body:**
```json
{ "username": "alice", "password": "secret123" }
```

**Login — lockout response (after 3 failed attempts):**
```json
{
  "success": false,
  "locked": true,
  "seconds_remaining": 57,
  "message": "Account locked due to multiple failed attempts. Please try again in 57 seconds."
}
```

---

### Contacts

All contact endpoints require an active session (login first).

| Method | Endpoint                        | Description                      |
|--------|---------------------------------|----------------------------------|
| GET    | `/api/contacts`                 | List all contacts for the user   |
| POST   | `/api/contacts`                 | Add a new contact                |
| PUT    | `/api/contacts/<id>`            | Update a contact by ID           |
| DELETE | `/api/contacts/<id>`            | Delete a contact by ID           |
| GET    | `/api/contacts/search?q=&field=`| Search contacts                  |

**Add/update contact — request body:**
```json
{
  "name": "John Doe",
  "phone": "9876543210",
  "email": "john@example.com"
}
```

**Contact object (in responses):**
```json
{
  "id": 1,
  "name": "John Doe",
  "phone": "9876543210",
  "email": "john@example.com",
  "date_added": "2024-01-15 10:30:00"
}
```

**Search parameters:**

| Parameter | Values                   | Description                         |
|-----------|--------------------------|-------------------------------------|
| `q`       | any string               | The search term                     |
| `field`   | `all`, `name`, `phone`, `email` | Field to search in (default: `all`) |

**Example:** `GET /api/contacts/search?q=john&field=name`

---

### Export

| Method | Endpoint           | Description                    |
|--------|--------------------|--------------------------------|
| GET    | `/api/export/csv`  | Download contacts as a CSV file |
| GET    | `/api/export/json` | Download contacts as a JSON file |

---

## Data Validation Rules

All validation is enforced server-side in `contacts/validators.py`.

**Username**
- Minimum 3 characters
- Only letters, numbers, and underscores (`a-z`, `A-Z`, `0-9`, `_`)

**Password**
- Minimum 6 characters

**Contact Name**
- 2–50 characters
- Only letters, spaces, apostrophes (`'`), and hyphens (`-`)
- Cannot start or end with a space, apostrophe, or hyphen
- No consecutive special characters
- Must contain at least 2 actual letters

**Phone Number** (Indian mobile format)
- Strips spaces, dashes, and parentheses before validation
- Strips `+91` or `91` country code prefix if present
- Must be exactly 10 digits after stripping
- Must start with 6, 7, 8, or 9

**Email**
- Optional field — can be left blank
- If provided, must match standard email format

---

## Security Notes

- **Passwords are stored in plain text.** For any real-world deployment, replace this with a proper hashing mechanism (e.g., `django.contrib.auth.hashers`).
- The `SECRET_KEY` in `settings.py` is a placeholder — replace it before deploying.
- Set `DEBUG = False` and configure `ALLOWED_HOSTS` properly in production.
- Consider adding HTTPS and setting `SESSION_COOKIE_SECURE = True` in production.

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
