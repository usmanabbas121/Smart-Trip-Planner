# Vercel Deployment Guide

## Environment Variables

Add these in Vercel Dashboard → Settings → Environment Variables:

1. **SECRET_KEY** - Django secret key
2. **DEBUG** - `False` for production
3. **ALLOWED_HOSTS** - `your-backend.vercel.app,*.vercel.app`
4. **CORS_ALLOWED_ORIGINS** - `https://your-frontend.vercel.app`
5. **OPENROUTE_SERVICE_API_KEY** - Optional

## Deployment Settings

- Root Directory: `backend`
- Framework Preset: Other
- Build Command: (empty)
- Output Directory: (empty)
- Install Command: `pip install -r requirements.txt`

## Frontend Configuration

Set environment variable in frontend Vercel project:
- **REACT_APP_API_URL**: `https://your-backend.vercel.app`
