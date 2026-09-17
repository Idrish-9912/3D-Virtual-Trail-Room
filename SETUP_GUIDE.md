# 3D Virtual Room - Development Setup Guide

## ✅ Completed Setup Steps

### System Requirements (Verified)
- ✓ Python 3.13.5 (requirement: 3.11+)
- ✓ Node.js v24.19.0
- ✓ npm 11.17.0
- ⚠ PostgreSQL not yet installed (required for database)

### Backend Setup (Completed)
- ✓ Virtual environment created at `3D-Backend/project/venv/`
- ✓ Dependencies installed: FastAPI, SQLAlchemy, Alembic, PyJWT, bcrypt, etc.
- ✓ `.env` configuration file created with development defaults
- ✓ Uploads directory created

### Frontend Setup (Completed)
- ✓ npm dependencies installed: React, Vite, Three.js, Tailwind, etc.
- ✓ `.env` configuration file created (API_URL = http://localhost:8000)

---

## 🚀 Next Steps - Running the Application

### Step 1: Set Up PostgreSQL (Required)

**Option A: Install PostgreSQL locally**
1. Download from https://www.postgresql.org/download/windows/
2. Run the installer and follow the setup wizard
3. Default port: 5432
4. Create a superuser (default: `postgres` / `postgres`)

**Option B: Use Docker (if installed)**
```bash
docker run --name postgres-dressing-room -e POSTGRES_PASSWORD=postgres -d -p 5432:5432 postgres:16
```

**Option C: Use a managed cloud database**
- AWS RDS, Azure Database for PostgreSQL, or similar
- Update `DATABASE_URL` in `.env` with your connection string

### Step 2: Create the Database

Once PostgreSQL is running, create the database:

**Via psql (command line):**
```bash
psql -U postgres -c "CREATE DATABASE dressing_room;"
```

**Via pgAdmin (GUI):**
1. Open pgAdmin
2. Right-click "Databases" → Create → Database
3. Name: `dressing_room`

### Step 3: Run Alembic Migrations

The migrations create all required tables (users, avatars, clothing, outfits, etc.).

```bash
cd "3D-Backend/project"
.\venv\Scripts\Activate.ps1
alembic upgrade head
```

Expected output:
```
INFO  [alembic.runtime.migration] Running upgrade  -> 0001_initial, initial
INFO  [alembic.runtime.migration] Running migration tokens
```

### Step 4: Start the Backend API

```bash
cd "3D-Backend/project"
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete
```

Visit http://localhost:8000/docs for interactive API documentation.

### Step 5: Start the Frontend Development Server

In a new terminal:

```bash
cd "3D-Frontend/project1"
npm run dev
```

Expected output:
```
VITE v5.4.2  ready in 123 ms

➜  Local:   http://localhost:5173/
```

Visit http://localhost:5173 in your browser.

---

## 📋 Environment Configuration

### Backend (.env)
```
APP_NAME=AI Virtual Dressing Room
API_V1_PREFIX=/api
BACKEND_CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/dressing_room
SECRET_KEY=your-super-secret-key-change-me-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
UPLOAD_DIR=uploads
MAX_UPLOAD_SIZE_MB=5
ALLOWED_IMAGE_TYPES=image/jpeg,image/png,image/webp
```

⚠️ **Security:** Change `SECRET_KEY` to a long random string:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Frontend (.env)
```
VITE_API_URL=http://localhost:8000
```

---

## 🧪 Testing the Setup

### Test Backend API
```bash
# Health check
curl http://localhost:8000/

# Expected response:
# {"app":"AI Virtual Dressing Room","status":"ok","docs":"/docs"}
```

### Test Database Connection
```bash
cd "3D-Backend/project"
python -c "from app.database.database import engine; print(engine.url)"
```

### Test Frontend
```bash
npm run build  # Verify production build works
```

---

## 📁 Project Structure Recap

```
3D-Virtual Room/
├── 3D-Backend/project/               # FastAPI REST API
│   ├── venv/                         # Virtual environment (created)
│   ├── .env                          # Configuration (created)
│   ├── uploads/                      # File uploads directory (created)
│   ├── app/
│   │   ├── main.py                   # FastAPI app entry point
│   │   ├── config.py                 # Settings
│   │   ├── database/                 # SQLAlchemy setup
│   │   ├── models/                   # ORM models (User, Avatar, etc.)
│   │   ├── routes/                   # API endpoints
│   │   ├── schemas/                  # Pydantic schemas
│   │   └── services/                 # Business logic
│   ├── alembic/                      # Database migrations
│   └── requirements.txt               # Python dependencies
│
├── 3D-Frontend/project1/             # React + Vite SPA
│   ├── node_modules/                 # NPM packages (installed)
│   ├── .env                          # Configuration (created)
│   ├── src/
│   │   ├── App.jsx                   # Root component
│   │   ├── main.jsx                  # React entry point
│   │   ├── pages/                    # Route pages
│   │   ├── components/               # React components
│   │   ├── context/                  # State management
│   │   └── services/                 # API client
│   ├── package.json                  # NPM dependencies
│   └── vite.config.js                # Vite bundler config
│
└── 3D-Blender/project3/              # Avatar generator
    ├── blender/
    │   ├── run_avatar.py             # CLI entry point
    │   └── avatar_generator/         # Modular avatar system
    └── src/                          # React Three.js viewer
```

---

## 🔧 Troubleshooting

### Port Already in Use
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process (example: PID 1234)
taskkill /PID 1234 /F
```

### Database Connection Error
```
Error: could not connect to server: Connection refused
```
- Verify PostgreSQL is running: `psql --version`
- Check DATABASE_URL in .env
- Restart PostgreSQL service

### CORS Errors
- Verify `BACKEND_CORS_ORIGINS` includes `http://localhost:5173`
- Restart backend server after .env changes

### Module Not Found (Python)
```bash
cd "3D-Backend/project"
.\venv\Scripts\Activate.ps1
pip list  # Check installed packages
pip install -r requirements.txt --upgrade
```

### NPM Install Issues
```bash
cd "3D-Frontend/project1"
npm cache clean --force
rm -r node_modules package-lock.json
npm install
```

---

## 📝 API Quick Reference

| Endpoint | Method | Auth | Purpose |
|----------|--------|------|---------|
| `POST /api/auth/login` | POST | No | User login |
| `POST /api/auth/register` | POST | No | User registration |
| `GET /api/users/me` | GET | Yes | Current user info |
| `POST /api/avatars` | POST | Yes | Create avatar |
| `GET /api/avatars` | GET | Yes | List user avatars |
| `PUT /api/avatars/{id}` | PUT | Yes | Update avatar |
| `DELETE /api/avatars/{id}` | DELETE | Yes | Delete avatar |
| `GET /api/clothing` | GET | Yes | Browse clothing |
| `POST /api/outfits` | POST | Yes | Create outfit |
| `POST /api/uploads` | POST | Yes | Upload image |

Access full API docs at: http://localhost:8000/docs

---

## 📚 Additional Resources

- FastAPI: https://fastapi.tiangolo.com/
- SQLAlchemy: https://www.sqlalchemy.org/
- React: https://react.dev/
- Vite: https://vitejs.dev/
- Three.js: https://threejs.org/
- PostgreSQL: https://www.postgresql.org/

---

## ✨ You're Ready!

After completing the steps above, you'll have:
- ✓ Backend API running on `http://localhost:8000`
- ✓ Frontend SPA running on `http://localhost:5173`
- ✓ Database ready for user/avatar/outfit data
- ✓ Full-stack 3D Virtual Dressing Room ready for development

**Next:** Open http://localhost:5173 and test user registration and avatar creation!
