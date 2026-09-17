# AI-Powered 3D Virtual Dressing Room — Backend API

A production-style backend built with **FastAPI**, **SQLAlchemy**, **Pydantic**, **JWT auth**, and **PostgreSQL**. It powers an AI-driven virtual dressing room where users create avatars, browse clothing, and assemble outfits.

---

## 1. Installation

### Prerequisites

- Python 3.11+
- PostgreSQL 14+ (running locally or reachable via a connection string)

### Clone & install dependencies

```bash
# (optional) create a virtual environment first — see step 2
pip install -r requirements.txt
```

---

## 2. Virtual environment setup

It is strongly recommended to use a virtual environment so project dependencies don't pollute your system Python.

**macOS / Linux**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

To leave the environment later: `deactivate`.

---

## 3. Environment variables

Copy the example file and fill in your values:

```bash
cp .env.example .env
```

| Variable | Description | Example |
|---|---|---|
| `APP_NAME` | Display name shown in docs | `AI Virtual Dressing Room` |
| `API_V1_PREFIX` | Route prefix for all APIs | `/api` |
| `BACKEND_CORS_ORIGINS` | Comma-separated allowed origins | `http://localhost:5173` |
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@localhost:5432/dressing_room` |
| `SECRET_KEY` | JWT signing secret (use a long random string) | `super-secret-change-me` |
| `ALGORITHM` | JWT algorithm | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token lifetime | `60` |
| `UPLOAD_DIR` | Where uploaded images are stored | `uploads` |
| `MAX_UPLOAD_SIZE_MB` | Max upload size | `5` |
| `ALLOWED_IMAGE_TYPES` | Allowed MIME types | `image/jpeg,image/png,image/webp` |

> The frontend runs separately at `http://localhost:5173`, which is already listed in `BACKEND_CORS_ORIGINS`.

---

## 4. Database setup

### Create the database

```bash
psql -U postgres -c "CREATE DATABASE dressing_room;"
```

### Run migrations

```bash
alembic upgrade head
```

This creates the `users`, `avatars`, `clothing`, `outfits`, and `outfit_items` tables.

To roll back the latest migration:

```bash
alembic downgrade -1
```

---

## 5. Running the FastAPI server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- **Swagger docs:** http://localhost:8000/docs
- **ReDoc docs:** http://localhost:8000/redoc
- **Health check:** http://localhost:8000/

---

## API Overview

All routes are prefixed with `/api`.

### Auth

| Method | Path | Description | Auth |
|---|---|---|---|
| POST | `/api/auth/register` | Create an account | No |
| POST | `/api/auth/login` | Get a JWT token (OAuth2 password flow) | No |
| GET | `/api/auth/me` | Current user profile | Yes |

### Avatars (owner-scoped)

| Method | Path | Description |
|---|---|---|
| POST | `/api/avatars` | Create an avatar |
| GET | `/api/avatars` | List your avatars |
| GET | `/api/avatars/{id}` | Get one avatar |
| PUT | `/api/avatars/{id}` | Update an avatar |
| DELETE | `/api/avatars/{id}` | Delete an avatar |

### Clothing (catalog, read-only)

| Method | Path | Description |
|---|---|---|
| GET | `/api/clothing` | List clothing |
| GET | `/api/clothing/{id}` | Get one item |
| GET | `/api/clothing/category/{category}` | Filter by category |

### Outfits (owner-scoped)

| Method | Path | Description |
|---|---|---|
| POST | `/api/outfits` | Create an outfit |
| GET | `/api/outfits` | List your outfits |
| GET | `/api/outfits/{id}` | Get one outfit |
| PUT | `/api/outfits/{id}` | Update an outfit |
| DELETE | `/api/outfits/{id}` | Delete an outfit |

### Uploads

| Method | Path | Description |
|---|---|---|
| POST | `/api/upload` | Upload an image (type + size validated) |

---

## Avatar Generation Pipeline

The avatar service (`app/services/avatar_service.py`) orchestrates:

```
Uploaded Image → Validation → Face Detection → Feature Extraction
              → Generate Avatar Parameters → Return Avatar Configuration
```

Placeholder functions live in `app/services/image_processor.py`:

- `validate_image()`
- `detect_face()`
- `extract_face_features()`
- `estimate_skin_color()`
- `estimate_face_shape()`

These are modular stubs designed so **MediaPipe** and **OpenCV** can be integrated later without changing the service layer.

---

## Project Structure

```
app/
  main.py              # FastAPI app, CORS, logging, route wiring
  config.py           # Pydantic settings from .env
  database/
    database.py        # Engine, SessionLocal, Base, get_db
    models.py          # Re-exports all models for Alembic
  models/
    user.py
    avatar.py
    clothing.py
    outfit.py          # Outfit + OutfitItem
  schemas/
    user.py
    avatar.py
    clothing.py
    outfit.py
    upload.py
  routes/
    auth.py
    users.py
    avatars.py
    clothing.py
    outfits.py
    uploads.py
  services/
    image_processor.py # CV placeholders
    avatar_service.py  # Pipeline orchestration
  utils/
    security.py        # Password hashing + JWT
    dependencies.py    # get_current_user
alembic/
  env.py
  versions/
    0001_initial.py
requirements.txt
.env.example
README.md
```
