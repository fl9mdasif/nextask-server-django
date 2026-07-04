# NexTask — Backend (Django)

A REST API backend for the NexTask full-stack application.  
Built with Django 6, Django REST Framework, JWT authentication, and SQLite.

---

## Tech Stack

| Tool | Purpose |
|---|---|
| Django 6 | Backend framework |
| Django REST Framework | API endpoints |
| djangorestframework-simplejwt | JWT authentication |
| django-cors-headers | Cross-origin requests |
| Pillow | Image upload handling |
| SQLite | Database |
| python-dotenv | Environment variables |

---

## Project Structure

```
nextask-server-django/
├── config/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── users/                   # Auth app (custom User model)
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── admin.py
├── tasks/                   # Task management app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── annotate/                # Image annotation app
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── venv/                    # Virtual environment (not in git)
├── manage.py
├── requirements.txt
└── .env                     # Environment variables (not in git)
```

---

## Requirements

- Python 3.12+
- pip

---

## How to Clone and Run

### Step 1 — Clone the repository

```bash
git clone https://github.com/fl9mdasif/nextask-server-django.git
cd nextask-server-django
```

### Step 2 — Create virtual environment

```bash
python -m venv venv
```

### Step 3 — Activate virtual environment

**Windows (PowerShell):**
```bash
venv\Scripts\activate
```

**Windows (CMD):**
```bash
venv\Scripts\activate.bat
```

**Mac / Linux:**
```bash
source venv/bin/activate
```

> ✅ You will see `(venv)` at the start of your terminal line when activated.  
> ⚠️ You must activate the virtual environment **every time** you open a new terminal.

### Step 4 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 5 — Create `.env` file

Create a `.env` file in the root directory:

```env
SECRET_KEY=django-insecure-your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 6 — Run migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 7 — Create a superuser (admin)

```bash
python manage.py createsuperuser
```

Enter your details:
- Email: `admin@gmail.com`
- Username: `admin`
- Password: `Admin123!`

### Step 8 — Run the server

```bash
python manage.py runserver
```

Server will start at: **http://127.0.0.1:8000**

---

## API Endpoints

### Auth
| Method | URL | Description |
|---|---|---|
| POST | `/api/auth/login/` | Login with email + password → returns JWT |
| POST | `/api/auth/refresh/` | Refresh access token |
| GET | `/api/auth/me/` | Get current logged-in user |
| POST | `/api/auth/logout/` | Logout (blacklist token) |

### Tasks
| Method | URL | Description |
|---|---|---|
| GET | `/api/tasks/?date=2026-07-04` | Get tasks filtered by date |
| POST | `/api/tasks/` | Create new task |
| GET | `/api/tasks/:id/` | Get single task |
| PATCH | `/api/tasks/:id/` | Update task |
| DELETE | `/api/tasks/:id/` | Delete task |
| PATCH | `/api/tasks/:id/reorder/` | Update status + order (drag & drop) |

### Annotate
| Method | URL | Description |
|---|---|---|
| GET | `/api/annotate/images/` | Get all uploaded images |
| POST | `/api/annotate/images/` | Upload new image |
| GET | `/api/annotate/images/:id/` | Get single image + its polygons |
| DELETE | `/api/annotate/images/:id/` | Delete image |
| GET | `/api/annotate/images/:id/polygons/` | Get all polygons for an image |
| POST | `/api/annotate/images/:id/polygons/` | Save new polygon |
| DELETE | `/api/annotate/polygons/:id/` | Delete specific polygon |

---

## Testing with Postman

### 1. Login
```
POST http://127.0.0.1:8000/api/auth/login/
Content-Type: application/json

{
  "email": "admin@gmail.com",
  "password": "*******"
}
```

Copy the `access` token from the response.

### 2. Use token in requests
Add this header to all protected endpoints:
```
Authorization: Bearer <your_access_token>
```

### 3. Create a task
```
POST http://127.0.0.1:8000/api/tasks/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "My first task",
  "priority": "high",
  "status": "todo",
  "due_date": "2026-07-04",
  "tags": ["work", "urgent"]
}
```

---

## Annotate API · Guide

> All annotate routes require a **Bearer token** — complete the Login step first.

### 4. Upload an Image

```
POST http://127.0.0.1:8000/api/annotate/images/
Authorization: Bearer <token>
Content-Type: multipart/form-data   ← use form-data in Postman (NOT JSON)
```

**form-data fields in Postman:**

| Key | Type | Value |
|---|---|---|
| `name` | Text | `chest-xray-001` |
| `image` | File | *(select a .jpg or .png from your computer)* |

**Expected response `201 Created`:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "chest-xray-001",
    "image": "http://127.0.0.1:8000/media/annotations/yourfile.jpg",
    "uploaded_at": "2026-07-04T17:00:00Z",
    "polygons": []
  }
}
```

> 📋 Copy the `id` from the response — you'll use it in the polygon routes below.

---

### 5. List All Images

```
GET http://127.0.0.1:8000/api/annotate/images/
Authorization: Bearer <token>
```

**Expected response `200 OK`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "chest-xray-001",
      "image": "http://127.0.0.1:8000/media/annotations/yourfile.jpg",
      "uploaded_at": "2026-07-04T17:00:00Z",
      "polygons": []
    }
  ]
}
```

---

### 6. Get Single Image (with all its polygons)

```
GET http://127.0.0.1:8000/api/annotate/images/1/
Authorization: Bearer <token>
```

**Expected response `200 OK`** — same structure as above. After saving polygons (step 7), they appear nested inside `polygons`.

---

### 7. Save a Polygon

```
POST http://127.0.0.1:8000/api/annotate/images/1/polygons/
Authorization: Bearer <token>
Content-Type: application/json
```

**Body:**
```json
{
  "points": [
    {"x": 100, "y": 150},
    {"x": 200, "y": 100},
    {"x": 250, "y": 200},
    {"x": 150, "y": 250}
  ],
  "label": "lung-nodule",
  "color": "#FF0000"
}
```

**Expected response `201 Created`:**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "points": [
      {"x": 100, "y": 150},
      {"x": 200, "y": 100},
      {"x": 250, "y": 200},
      {"x": 150, "y": 250}
    ],
    "label": "lung-nodule",
    "color": "#FF0000",
    "created_at": "2026-07-04T17:05:00Z"
  }
}
```

> 📋 Copy the polygon `id` — needed for delete.

---

### 8. List Polygons for an Image

```
GET http://127.0.0.1:8000/api/annotate/images/1/polygons/
Authorization: Bearer <token>
```

**Expected response `200 OK`:**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "points": [{"x": 100, "y": 150}, "..."],
      "label": "lung-nodule",
      "color": "#FF0000",
      "created_at": "2026-07-04T17:05:00Z"
    }
  ]
}
```

---

### 9. Delete a Polygon

```
DELETE http://127.0.0.1:8000/api/annotate/polygons/1/
Authorization: Bearer <token>
```

**Expected response `200 OK`:**
```json
{
  "success": true,
  "message": "Polygon deleted"
}
```

---

### 10. Delete an Image

```
DELETE http://127.0.0.1:8000/api/annotate/images/1/
Authorization: Bearer <token>
```

**Expected response `200 OK`:**
```json
{
  "success": true,
  "message": "Image deleted"
}
```

---

### 11. Security Test — User Isolation

Try fetching an image ID that belongs to a **different user**:

```
GET http://127.0.0.1:8000/api/annotate/images/999/
Authorization: Bearer <other_user_token>
```

**Expected response `404 Not Found`:**
```json
{
  "success": false,
  "message": "Image not found"
}
```

✅ Confirms no cross-user data leaks.

---

> ⚠️ Always add a trailing slash `/` at the end of URLs. Django requires it.

---

## Admin Panel

Visit **http://127.0.0.1:8000/admin/** and login with your superuser credentials to manage data directly.

---

## Difficulties & How I Solved Them

### 1. Prisma → Django mindset shift
Coming from a Node.js/Express background, Django's structure was different.  
**Solution:** Mapped concepts — `models.py` = Mongoose schema, `views.py` = controller, `urls.py` = router, `migrations` = Prisma migrate.

### 2. Custom User model with email login
Django's default `User` uses `username` for auth, but we needed email-based login.  
**Solution:** Created a custom `User` model extending `AbstractUser` with `USERNAME_FIELD = 'email'` and used `get_user_model()` everywhere instead of importing `User` directly.

### 3. JWT authenticate() not working
`authenticate()` was failing because it was passing `username` instead of `email`.  
**Solution:** Changed to `authenticate(request, email=email, password=password)`.

### 4. DELETE/PATCH returning 500 error
Django's `APPEND_SLASH` setting was rejecting requests without trailing slash.  
**Solution:** Always use trailing slash in URLs — `/api/tasks/1/` not `/api/tasks/1`.

### 5. `No module named 'django'` error
Forgot to activate virtual environment after opening a new terminal.  
**Solution:** Always run `venv\Scripts\activate` before any Django command.

---

## Python Version

```
Python 3.12
Django 6.0.6
```

Check your version:
```bash
python --version
```