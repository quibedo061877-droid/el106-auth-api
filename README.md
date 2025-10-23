# EL106 Authentication API (Django + DRF)

Author: Arsenio A. Quibedo Jr
Contact: nonicksquibedo@gmail.com

A RESTful API and GUI system built with Django REST Framework for MIT EL106.

## Features

- User Registration (with email verification)
- JWT Login / Logout
- Protected Profile (via JWT)
- Password Reset (email link)
- Swagger API Docs
- Simple HTML + CSS GUI (light theme)

## Project Setup

1. Clone the repository and navigate to the project folder:
```bash
git clone <repo-url>
cd el106_auth_api
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install django djangorestframework djangorestframework-simplejwt drf-yasg django-cors-headers
```

4. Run migrations and start the server:
```bash
python manage.py migrate
python manage.py runserver
```

5. Open in your browser:
- GUI Home: http://localhost:8000/
- Register: http://localhost:8000/register/
- Login: http://localhost:8000/login/
- Profile: http://localhost:8000/profile/
- Swagger: http://localhost:8000/swagger/

## Notes

- Emails (verification & reset links) are printed to the console by default (development).
- Database: SQLite (default for quick setup).
- To use real email sending, configure SMTP settings in `el106_auth_api/settings.py`.

## Common Flows

### Register & Verify
1. Register at `/register/`.
2. Check console for verification link like:
```
http://localhost:8000/verify-email/?uid=1&token=<token>
```
3. Visit the link to activate the account.

### JWT Login & Profile (API)
1. Obtain token:
```
POST /api/token/  { "username": "youruser", "password": "..." }
```
2. Use `Authorization: Bearer <access_token>` to access:
```
GET /api/profile/
```

## Demo Video Suggestions

- Show GUI: register -> verify -> login -> profile
- Show Swagger: obtain token -> call `/api/profile/`
- Show password reset flow

