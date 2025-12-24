# Vercel Deployment Guide for Django Backend

## Environment Variables Required in Vercel

Vercel dashboard mein jao: **Settings → Environment Variables** aur yeh add karo:

### Required Variables:

1. **SECRET_KEY**
   - Value: Apna Django secret key (ek strong random string)
   - Example: `django-insecure-ch3u%e&bw7hlgko6*_^nig6&g7ohj0ivm3mn%v*x%wh(@!u@yq`
   - **Important:** Production mein strong secret key use karo!

2. **DEBUG**
   - Value: `False` (Production ke liye)
   - Development: `True`

3. **ALLOWED_HOSTS**
   - Value: `tripspotter.vercel.app,your-custom-domain.com` (comma-separated)
   - Apne Vercel domain ko add karo

4. **CORS_ALLOWED_ORIGINS**
   - Value: `https://tripspotter.vercel.app,https://your-frontend-domain.vercel.app` (comma-separated)
   - Frontend domain ko add karo

5. **OPENROUTE_SERVICE_API_KEY** (Optional)
   - Value: Apna OpenRouteService API key
   - Agar nahi hai toh empty rakh sakte ho

## Deployment Steps:

1. **GitHub se connect karo:**
   - Vercel dashboard mein project create karo
   - GitHub repository connect karo

2. **Root Directory set karo:**
   - Vercel project settings mein
   - Root Directory: `backend` (agar backend folder se deploy kar rahe ho)
   - Ya root directory: `.` (agar root se deploy kar rahe ho)

3. **Build Settings:**
   - Framework Preset: Other
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

4. **Environment Variables add karo** (upar wale)

5. **Deploy!**

## Important Notes:

- Vercel serverless functions use karta hai, isliye Django ko properly configure kiya gaya hai
- Database: SQLite file-based hai, har deployment mein reset ho sakta hai
- Agar persistent database chahiye, PostgreSQL add-on use karo (Vercel Postgres)

## Frontend Configuration:

Frontend mein `api.ts` file mein backend URL update karo:

```typescript
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://your-backend.vercel.app';
```

Frontend Vercel project mein environment variable:
- **REACT_APP_API_URL**: `https://your-backend.vercel.app`


