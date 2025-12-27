# Django Backend

## Setup

1. Create `.env` file in `backend/` folder:
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
