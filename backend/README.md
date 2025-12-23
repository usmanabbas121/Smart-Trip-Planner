# Django Backend - Vercel Deployment

## Vercel Project Settings

Jab Vercel mein project create karte ho, yeh settings use karo:

### Root Directory
- **Root Directory:** `backend` (ya `.` agar backend folder hi root hai)

### Build Settings
- **Framework Preset:** Other
- **Build Command:** (empty - leave blank)
- **Output Directory:** (empty - leave blank)
- **Install Command:** `pip install -r requirements.txt`

## Environment Variables (Vercel Dashboard)

Vercel Project Settings → Environment Variables mein yeh add karo:

1. **SECRET_KEY**
   - Production ke liye strong secret key
   - Example: Generate karo: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`

2. **DEBUG**
   - Value: `False` (Production)
   - Development: `True`

3. **ALLOWED_HOSTS**
   - Value: `your-backend.vercel.app,*.vercel.app`
   - Comma-separated list

4. **CORS_ALLOWED_ORIGINS**
   - Value: `https://your-frontend.vercel.app,https://tripspotter.vercel.app`
   - Frontend domains (comma-separated)

5. **OPENROUTE_SERVICE_API_KEY** (Optional)
   - OpenRouteService API key (agar hai)

## Local Development

1. `.env` file create karo `backend/` folder mein:
```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://localhost:3000
OPENROUTE_SERVICE_API_KEY=your-key
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run server:
```bash
python manage.py runserver
```

## API Endpoints

- `POST /api/calculate-trip/` - Calculate trip route and generate log sheets

