# Dashboard Flow - After Registration

## What Happens When User Registers

```
User clicks "Create Account" (with name, email, password)
        ↓
Backend creates user in database
        ↓
JWT token generated & returned
        ↓
Token stored in browser localStorage
        ↓
User redirected to /dashboard
        ↓
Dashboard shows user profile & avatar management
```

## Dashboard Page Elements

### 1. User Profile Section
- Welcome message: "Welcome, Test User!"
- User email displayed
- Total avatars count (starts at 0)
- Total outfits count (starts at 0)

### 2. My Avatars Grid
- **Empty state initially** (no avatars yet)
- Shows message: "No avatars yet. Create your first digital twin!"
- Button: "Create New Avatar"
- Once created, shows:
  - Avatar thumbnail (3D preview)
  - Avatar name
  - Creation date
  - Options: Edit, View, Delete

### 3. Saved Outfits Grid
- **Empty state initially**
- Shows message: "No outfits saved yet. Create your first look!"
- Button: "Create Outfit"

### 4. Navigation Bar
- VirtualFit logo (clickable → home)
- User menu (name + logout button)
- Links: Dashboard, Avatar Creator, Dressing Room

---

## Flow: Creating Your First Avatar

```
User at Dashboard
        ↓
Clicks "Create New Avatar" button
        ↓
Navigates to /avatar-creator
        ↓
User customizes:
  - Body type (dropdown)
  - Face shape (dropdown)
  - Hair style & color (customizers)
  - Skin tone (color picker)
        ↓
Real-time 3D preview updates
        ↓
User can upload photo for AI generation (optional)
        ↓
User clicks "Save Avatar"
        ↓
Avatar stored in database
        ↓
Redirected back to /dashboard
        ↓
Avatar appears in "My Avatars" grid
```

---

## API Endpoints Used

### Registration Flow
```
POST /api/register
  ├─ Body: { name, email, password }
  └─ Response: { token, user: { id, email, name } }

GET /api/auth/me (with JWT token)
  └─ Response: { id, email, name, avatars[], outfits[] }
```

### Avatar Management
```
POST /api/avatars (with JWT token)
  ├─ Body: { name, body_type, hair_style, face_shape, skin_color, hair_color }
  └─ Response: { id, user_id, name, model_url, created_at }

GET /api/avatars (with JWT token)
  └─ Response: [{ id, name, model_url, ... }, ...]

PUT /api/avatars/{id} (with JWT token)
  └─ Update avatar customization

DELETE /api/avatars/{id} (with JWT token)
  └─ Delete avatar
```

### Outfit Management
```
POST /api/outfits (with JWT token)
  ├─ Body: { avatar_id, outfit_items: [clothing_id, ...] }
  └─ Response: { id, avatar_id, created_at }

GET /api/outfits (with JWT token)
  └─ Response: [{ id, avatar_id, items[], ... }, ...]
```

### Image Upload (for AI Avatar Generation)
```
POST /api/uploads (with JWT token)
  ├─ Body: FormData with image file
  └─ Response: { url, filename, size }
```

---

## Database Structure After Registration

### Users Table
```
id   | name      | email                | password_hash | created_at
-----|-----------|----------------------|---------------|-------------
1    | Test User | test123@example.com  | [hashed]      | 2026-08-30 ...
```

### Avatars Table (Empty Initially)
```
id | user_id | name | body_type | hair_style | ... | model_url | created_at
---|---------|------|-----------|------------|----|-----------|----------
(empty - user must create)
```

### Outfits Table (Empty Initially)
```
id | user_id | created_at
---|---------|----------
(empty - user must create)
```

---

## Status After Setup

✅ **Account Created**
✅ **Authentication Working** (JWT token)
✅ **User Profile Ready**
❌ **No Avatars Yet** (must be created manually)
❌ **No Outfits Yet** (must be created after avatars)

---

## Next Steps for User

1. **Navigate to Dashboard** → See their profile
2. **Click "Create New Avatar"** → Go to Avatar Creator
3. **Customize Avatar** → Choose body, face, hair, colors
4. **Save Avatar** → Stored in database
5. **Go to Dressing Room** → Use avatar with clothing
6. **Create Outfits** → Save favorite looks
