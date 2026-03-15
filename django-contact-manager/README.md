# Contact Manager — Django Edition

This is a **1:1 Django conversion** of the original Flask + React contact manager application.
All features, validation rules, session behaviour, and API contracts are preserved exactly.

---

## Project Structure

```
django-contact-manager/
├── manage.py
├── requirements.txt
├── README.md
│
├── contact_manager/          # Django project package
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── contacts/                 # Django app (all backend logic)
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py             # AppUser, Contact
│   ├── views.py              # All API views (auth + contacts + export)
│   ├── urls.py               # URL routing
│   └── validators.py         # Same validators as original Flask project
│
├── templates/
│   └── index.html            # SPA shell (after React build)
│
└── frontend/                 # Original React + Vite project (unchanged)
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── main.jsx
        ├── index.css
        ├── services/api.js
        ├── contexts/AuthContext.jsx
        ├── components/
        │   ├── Sidebar.jsx
        │   ├── ContactForm.jsx
        │   └── ConfirmDialog.jsx
        └── pages/
            ├── AuthPage.jsx
            ├── Dashboard.jsx
            ├── ContactList.jsx
            ├── AddContact.jsx
            └── SearchContacts.jsx
```

---

## What Changed (Flask → Django)

| Flask | Django |
|-------|--------|
| `app.py` + Blueprints | `contact_manager/urls.py` + `contacts/urls.py` |
| `database.py` + raw MySQL | Django ORM with `AppUser` and `Contact` models |
| `operations.py` | Logic moved into `contacts/views.py` |
| Per-user tables (`contacts_<username>`) | Single `contacts` table with ForeignKey to `users` |
| `flask.session` | `django.contrib.sessions` (same cookie behaviour) |
| `flask_cors` | `django-cors-headers` |
| `pandas` for CSV export | Python's built-in `csv` module |

**The frontend (React + Vite) is 100% unchanged.** It still talks to `/api/*` endpoints
with the exact same request/response shapes.

---

## Setup Instructions

### 1. Install Python dependencies

```bash
pip install -r requirements.txt
```

> If `mysqlclient` fails to install, use PyMySQL instead:
> ```bash
> pip install PyMySQL
> ```
> Then add to `contact_manager/__init__.py`:
> ```python
> import pymysql
> pymysql.install_as_MySQLdb()
> ```

### 2. Configure MySQL

Edit `contact_manager/settings.py` or set environment variables:

```bash
export DB_NAME=contact_manager_db
export DB_USER=root
export DB_PASSWORD=yourpassword
export DB_HOST=localhost
```

Make sure the database exists (Django does NOT auto-create the database):
```sql
CREATE DATABASE contact_manager_db CHARACTER SET utf8mb4;
```

### 3. Run migrations

```bash
python manage.py makemigrations contacts
python manage.py migrate
```

> This creates the `users` and `contacts` tables automatically.

### 4. Start the Django backend

```bash
python manage.py runserver 5000
```

(Port 5000 matches the original Flask project. Use any port you like.)

### 5. Start the React frontend (development)

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server runs on **http://localhost:3000** and proxies `/api/*` to
`http://localhost:5000` (configured in `frontend/vite.config.js`).

---

## API Endpoints (identical to original Flask project)

### Auth
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/api/register` | Create account |
| POST | `/api/login` | Sign in (with lockout after 3 failures) |
| POST | `/api/logout` | Sign out |
| GET | `/api/me` | Get current session user |

### Contacts
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/contacts` | List all contacts |
| POST | `/api/contacts` | Add a contact |
| PUT | `/api/contacts/<id>` | Update a contact |
| DELETE | `/api/contacts/<id>` | Delete a contact |
| GET | `/api/contacts/search?q=<term>&field=<all\|name\|phone\|email>` | Search |

### Export
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/api/export/csv` | Download contacts as CSV |
| GET | `/api/export/json` | Download contacts as JSON |

---

## Features Preserved

- ✅ User registration & login with session-based auth
- ✅ Account lockout after 3 failed attempts (60-second timer)
- ✅ Per-user contact isolation
- ✅ Contact CRUD (Create, Read, Update, Delete)
- ✅ Full-text search by name / phone / email
- ✅ Export to CSV and JSON
- ✅ Indian phone number validation (+91 stripping)
- ✅ Duplicate phone/email detection per user
- ✅ All original validators (username, password, name, phone, email)
- ✅ Same JSON API contract — frontend works without any changes
