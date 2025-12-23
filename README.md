# ELD Trip Planner

Full-stack application for calculating truck trip routes with HOS-compliant rest stops and generating ELD log sheets.

## Tech Stack

- **Backend**: Django 5.2 + Django REST Framework
- **Frontend**: React 18 + TypeScript
- **Map API**: OpenRouteService (free)
- **Map Library**: Leaflet + React-Leaflet

## Setup

### Backend

1. **Get OpenRouteService API Key (Optional but Recommended)**
   - Visit https://openrouteservice.org/dev/#/signup
   - Sign up for a free account (2,000 requests/day)
   - Copy your API key
   - Set it as an environment variable:
     ```bash
     export OPENROUTE_SERVICE_API_KEY="your-api-key-here"
     ```
   - Note: The app will work without an API key for limited testing, but you may hit rate limits.

2. **Install and Run**
   ```bash
   cd backend
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

### Frontend

```bash
cd frontend
npm install
npm start
```

## API Endpoints

- `POST /api/calculate-trip/` - Calculate trip route and generate log sheets

## Features

- Route calculation with fuel stops (every 1000 miles)
- HOS compliance checking (70-hour/8-day rule)
- Automatic rest break calculation (30-min after 8 hours driving, 10-hour rest)
- ELD log sheet generation matching DOT format
- Interactive map visualization
- Multiple log sheets for multi-day trips

