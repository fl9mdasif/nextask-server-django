# NexTask — CLAUDE.md
> Full-stack project brief for AI assistant (Antigravity / Claude Code).
> Read this fully before writing any code.

---

## Project Identity

- **Name:** NexTask
- **Assignment from:** Vai Radiology LLC (US-based remote)
- **Developer:** Md Asif Al Azad

---

## What We Are Building

A 2-in-1 web app:
1. **Kanban Task Manager** (`/tasks`) — manage tasks by date with drag & drop
2. **Image Annotation Tool** (`/annotate`) — upload images, draw polygons, save to DB
3. **Login Page** (`/login`) — email + password auth

---

## Tech Stack

### Frontend
| Tool | Purpose |
|---|---|
| Next.js 16 (App Router) | Framework |
| TypeScript | Language (mandatory) |
| Tailwind CSS | Styling |
| Zustand | Global state (date, tasks, images) |
| @dnd-kit | Drag and drop for Kanban |
| react-konva / Konva.js | Canvas drawing for annotation |
| Axios | API calls to Django backend |
| date-fns | Date formatting |
| lucide-react | Icons |

### Backend
| Tool | Purpose |
|---|---|
| Django | Backend framework (mandatory) |
| Django REST Framework | API endpoints |
| djangorestframework-simplejwt | JWT auth |
| django-cors-headers | Allow Next.js to call Django |
| Pillow | Image upload handling |
| SQLite | Default Django DB (acceptable) |

### Deployment
| What | Where |
|---|---|
| Frontend | Vercel |
| Backend | PythonAnywhere |
| Media files (images) | Cloudinary (free tier) |

---

## Folder Structure

```
nextask/
├── frontend/                        # Next.js app
│   ├── app/
│   │   ├── login/
│   │   │   └── page.tsx
│   │   ├── tasks/
│   │   │   └── page.tsx
│   │   └── annotate/
│   │       └── page.tsx
│   ├── components/
│   │   ├── auth/
│   │   │   └── LoginForm.tsx
│   │   ├── tasks/
│   │   │   ├── Board.tsx            # Kanban board wrapper
│   │   │   ├── Column.tsx           # To Do / In Progress / Done
│   │   │   ├── TaskCard.tsx         # Individual task card
│   │   │   ├── TaskModal.tsx        # Add / Edit task modal
│   │   │   └── DateSelector.tsx     # Shared reusable date picker
│   │   └── annotate/
│   │       ├── ImageUploader.tsx    # Upload image to backend
│   │       ├── ImageSlider.tsx      # Scroll through uploaded images
│   │       └── AnnotationCanvas.tsx # Draw polygons with Konva
│   ├── store/
│   │   ├── taskStore.ts             # Zustand: selected date, tasks
│   │   └── annotateStore.ts         # Zustand: images, polygons, active image
│   ├── lib/
│   │   └── api.ts                   # Axios instance + all API functions
│   └── middleware.ts                # Protect /tasks and /annotate routes
│
└── backend/                         # Django project
    ├── manage.py
    ├── requirements.txt
    ├── .env                         # SECRET_KEY, CORS origins, Cloudinary keys
    ├── config/                      # Django project config
    │   ├── settings.py
    │   ├── urls.py
    │   └── wsgi.py
    ├── tasks/                       # Tasks Django app
    │   ├── models.py
    │   ├── serializers.py
    │   ├── views.py
    │   └── urls.py
    └── annotate/                    # Annotate Django app
        ├── models.py
        ├── serializers.py
        ├── views.py
        └── urls.py
```

---

## Database Models

### tasks/models.py
```python
from django.db import models
from django.contrib.auth.models import User

class Task(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
    ]
    STATUS_CHOICES = [
        ('todo', 'To Do'),
        ('inprogress', 'In Progress'),
        ('done', 'Done'),
    ]

    user       = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tasks')
    title      = models.CharField(max_length=200)
    priority   = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    status     = models.CharField(max_length=20, choices=STATUS_CHOICES, default='todo')
    due_date   = models.DateField()
    tags       = models.JSONField(default=list, blank=True)
    order      = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['order', 'created_at']
```

### annotate/models.py
```python
from django.db import models
from django.contrib.auth.models import User

class AnnotationImage(models.Model):
    user        = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image       = models.ImageField(upload_to='annotations/')
    name        = models.CharField(max_length=200)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

class Polygon(models.Model):
    image      = models.ForeignKey(AnnotationImage, on_delete=models.CASCADE, related_name='polygons')
    points     = models.JSONField()   # [{"x": 10, "y": 20}, {"x": 50, "y": 80}, ...]
    label      = models.CharField(max_length=100, blank=True)
    color      = models.CharField(max_length=20, default='#FF0000')
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## API Endpoints

### Auth
| Method | URL | Purpose |
|---|---|---|
| POST | `/api/auth/login/` | Login → returns access + refresh JWT |
| POST | `/api/auth/refresh/` | Refresh access token |
| POST | `/api/auth/logout/` | Logout (blacklist token) |
| GET | `/api/auth/me/` | Get current user info |

### Tasks
| Method | URL | Purpose |
|---|---|---|
| GET | `/api/tasks/?date=2026-07-04` | Get all tasks for a specific date |
| POST | `/api/tasks/` | Create new task |
| PATCH | `/api/tasks/:id/` | Update task (title, status, priority, tags) |
| PATCH | `/api/tasks/:id/reorder/` | Update order + status after drag & drop |
| DELETE | `/api/tasks/:id/` | Delete task |

### Annotate
| Method | URL | Purpose |
|---|---|---|
| GET | `/api/annotate/images/` | Get all uploaded images |
| POST | `/api/annotate/images/` | Upload new image |
| DELETE | `/api/annotate/images/:id/` | Delete image |
| GET | `/api/annotate/images/:id/polygons/` | Get polygons for an image |
| POST | `/api/annotate/images/:id/polygons/` | Save new polygon |
| DELETE | `/api/annotate/polygons/:id/` | Delete specific polygon |

---

## Pages & Features

### 0. Login Page (`/login`)
- Email + password form
- On success → store JWT in httpOnly cookie or localStorage
- Redirect to `/tasks`
- If already logged in → redirect away from `/login`

### 1. Kanban Board (`/tasks`)
- `<DateSelector/>` at top — reusable date picker component
- Selected date stored in Zustand (`taskStore`)
- 3 columns: **To Do | In Progress | Done**
- Tasks fetched from backend filtered by selected date
- **Drag & Drop** between columns using `@dnd-kit`
  - On drop → PATCH request to update `status` + `order`
- **Add Task** button per column → opens `<TaskModal/>`
- **Edit Task** → click task card → opens `<TaskModal/>` prefilled
- **Delete Task** → button inside modal or card
- Each task card shows: title, priority badge, due date, tags
- Empty state if no tasks for selected date
- All task data persisted to Django backend

### 2. Image Annotation (`/annotate`)
- Upload image → POST to backend → stored with Pillow
- Scroll/slide through uploaded images (`<ImageSlider/>`)
- Click image → opens `<AnnotationCanvas/>` (Konva.js)
- Draw polygon by clicking points on canvas
  - Click to add point
  - Close polygon by clicking first point or pressing Enter
- Drawn polygons shown as colored overlays
- Click a polygon → option to delete it
- All polygons saved to backend on draw/delete
- Polygons loaded from backend when switching images

---

## Frontend Component Specs

### `<DateSelector/>`
```typescript
// Props
interface DateSelectorProps {
  selected: Date
  onChange: (date: Date) => void
}
// Must be reusable — used in tasks page
// Date state lives in Zustand, not inside this component
```

### `<Board/>`
```typescript
// Renders 3 <Column/> components
// Wraps with DndContext from @dnd-kit
// Handles onDragEnd → calls API to update status + order
```

### `<Column/>`
```typescript
interface ColumnProps {
  title: 'To Do' | 'In Progress' | 'Done'
  status: 'todo' | 'inprogress' | 'done'
  tasks: Task[]
}
```

### `<TaskCard/>`
```typescript
interface TaskCardProps {
  task: Task
  onEdit: (task: Task) => void
  onDelete: (id: number) => void
}
// Draggable via @dnd-kit useSortable hook
```

### `<TaskModal/>`
```typescript
interface TaskModalProps {
  mode: 'create' | 'edit'
  task?: Task        // prefilled if edit mode
  status: string     // column it belongs to
  onClose: () => void
  onSave: () => void
}
// Fields: title, priority (select), due date, tags (input with enter to add)
```

### `<AnnotationCanvas/>`
```typescript
interface AnnotationCanvasProps {
  image: AnnotationImage
  polygons: Polygon[]
  onPolygonSave: (points: Point[]) => void
  onPolygonDelete: (id: number) => void
}
// Uses react-konva Stage, Layer, Image, Line
```

---

## Zustand Stores

### taskStore.ts
```typescript
interface TaskStore {
  selectedDate: Date
  setSelectedDate: (date: Date) => void
  tasks: Task[]
  setTasks: (tasks: Task[]) => void
  fetchTasks: (date: string) => Promise<void>
}
```

### annotateStore.ts
```typescript
interface AnnotateStore {
  images: AnnotationImage[]
  activeImage: AnnotationImage | null
  polygons: Polygon[]
  setActiveImage: (image: AnnotationImage) => void
  fetchImages: () => Promise<void>
  fetchPolygons: (imageId: number) => Promise<void>
}
```

---

## Auth Flow

```
User visits /tasks
  → middleware.ts checks for JWT token
  → No token? redirect to /login
  → Has token? allow

Login form submits
  → POST /api/auth/login/ { email, password }
  → Django returns { access, refresh }
  → Store access token (localStorage or cookie)
  → Set Authorization: Bearer <token> header on all Axios requests
  → Redirect to /tasks
```

---

## Django Settings Checklist

```python
INSTALLED_APPS = [
    ...
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'tasks',
    'annotate',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # must be FIRST
    ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://your-vercel-app.vercel.app",
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
```

---

## Steps — Follow In Order

### ✅ Step 1 — Django Project Setup
```bash
mkdir nextask && cd nextask && mkdir backend frontend
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
pip install django djangorestframework djangorestframework-simplejwt pillow django-cors-headers python-dotenv
django-admin startproject config .
python manage.py startapp tasks
python manage.py startapp annotate
pip freeze > requirements.txt
```

### 👉 Step 2 — Settings + .env
- Configure `config/settings.py` (INSTALLED_APPS, CORS, JWT, MEDIA)
- Create `.env` with SECRET_KEY
- Create `.gitignore`

### Step 3 — Models + Migrations
- Write `tasks/models.py` (Task model)
- Write `annotate/models.py` (AnnotationImage + Polygon models)
- Run `python manage.py makemigrations`
- Run `python manage.py migrate`
- Run `python manage.py createsuperuser`

### Step 4 — Auth API
- Use Django's built-in User model
- Configure `config/urls.py` with JWT endpoints
- Create `GET /api/auth/me/` view
- Test with Postman: login → get token

### Step 5 — Tasks API
- Write `tasks/serializers.py`
- Write `tasks/views.py` (CRUD + filter by date + reorder)
- Write `tasks/urls.py`
- Connect to `config/urls.py`
- Test all endpoints

### Step 6 — Annotate API
- Write `annotate/serializers.py`
- Write `annotate/views.py` (image upload + polygon CRUD)
- Write `annotate/urls.py`
- Connect to `config/urls.py`
- Test image upload + polygon save

### Step 7 — Next.js Frontend Setup
```bash
cd ../frontend
npx create-next-app@latest . --typescript --tailwind --app
npm install zustand @dnd-kit/core @dnd-kit/sortable axios date-fns lucide-react react-konva konva
```

### Step 8 — Login Page
- `LoginForm.tsx` component
- Call POST `/api/auth/login/`
- Store JWT, redirect to `/tasks`
- `middleware.ts` route protection

### Step 9 — Kanban Board (/tasks)
- `DateSelector`, `Board`, `Column`, `TaskCard`, `TaskModal`
- Zustand taskStore
- Wire up all CRUD + drag & drop

### Step 10 — Annotation Tool (/annotate)
- `ImageUploader`, `ImageSlider`, `AnnotationCanvas`
- Konva polygon drawing
- Save/delete polygons via API

### Step 11 — Deploy Backend → PythonAnywhere
- Push to GitHub
- PythonAnywhere → Web tab → Manual config → Django
- Run migrations on server
- Set ALLOWED_HOSTS

### Step 12 — Deploy Frontend → Vercel
- Push frontend to GitHub
- Vercel → import repo
- Set `NEXT_PUBLIC_API_URL` env variable

### Step 13 — README + Video
- Backend README: setup steps, difficulties, Python version
- Frontend README: setup steps, Node version
- 2-minute demo video (Loom or OBS)

---

## Environment Variables

### backend/.env
```
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
```

### frontend/.env.local
```
NEXT_PUBLIC_API_URL=http://127.0.0.1:8000
```

---

## Git Setup

```bash
# Root level
cd nextask
git init
echo "backend/venv/" >> .gitignore
echo "backend/db.sqlite3" >> .gitignore
echo "backend/media/" >> .gitignore
echo "frontend/.next/" >> .gitignore
echo "frontend/node_modules/" >> .gitignore
echo ".env" >> .gitignore

git add .
git commit -m "initial: project structure"
git remote add origin https://github.com/yourusername/nextask.git
git push -u origin main
```

---

## Notes for AI Assistant

- Developer knows Express/Node well — use that as reference when explaining Django concepts
- `views.py` = controller, `urls.py` = router, `models.py` = mongoose schema, `migrations` = prisma migrate
- Always use `IsAuthenticated` permission on all views
- Filter tasks by `due_date` AND `user` — never return other users' data
- Polygon `points` stored as JSON array: `[{"x": 10, "y": 20}, ...]`
- Use DRF `ModelViewSet` where possible to reduce boilerplate
- Keep serializers thin — no business logic inside them
- All API responses follow: `{ success: true, data: {...} }` pattern