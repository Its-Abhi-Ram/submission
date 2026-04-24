# SkillBridge Attendance Management API
Change framework layers like Django and MySql
This is a Django REST API for managing attendance in the SkillBridge program. It implements role-based access control with JWT authentication.

## Live API Base URL
http://localhost:8000/api/ (for local development)

## Live Render Server URL:
Render Web server link : https://submission-5ujh.onrender.com

## Local Setup Instructions

1. Clone the repository and navigate to the project directory.
2. Install Python 3.8+ if not already installed.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Set up the database:
   ```
   python manage.py migrate
   python manage.py seed
   ```
5. Run the development server:
   ```
   python manage.py runserver
   ```

## Test Accounts

- **Student**: email: student1@example.com, password: password123
- **Trainer**: email: trainer1@example.com, password: password123
- **Institution**: email: institution@example.com, password: password123
- **Programme Manager**: email: pm@example.com, password: password123
- **Monitoring Officer**: email: mo@example.com, password: password123

## Sample curl Commands

### Signup
```bash
curl -X POST http://localhost:8000/api/auth/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Student",
    "email": "newstudent@example.com",
    "password": "password123",
    "role": "student",
    "institution_id": 1
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "student1@example.com",
    "password": "password123"
  }'
```

### Get Monitoring Token (for Monitoring Officer)
```bash
curl -X POST http://localhost:8000/api/auth/monitoring-token/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"key": "test_api_key"}'
```

### Create Batch (Trainer/Institution)
```bash
curl -X POST http://localhost:8000/api/batches/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Batch",
    "institution": 1
  }'
```

### Join Batch (Student)
```bash
curl -X POST http://localhost:8000/api/batches/join/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"token": "<invite_token>"}'
```

### Create Session (Trainer)
```bash
curl -X POST http://localhost:8000/api/sessions/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "batch": 1,
    "title": "Session Title",
    "date": "2024-01-01",
    "start_time": "09:00:00",
    "end_time": "10:00:00"
  }'
```

### Mark Attendance (Student)
```bash
curl -X POST http://localhost:8000/api/attendance/mark/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": 1,
    "status": "present"
  }'
```

### Get Session Attendance (Trainer)
```bash
curl -X GET http://localhost:8000/api/sessions/1/attendance/ \
  -H "Authorization: Bearer <access_token>"
```

### Get Batch Summary (Institution)
```bash
curl -X GET http://localhost:8000/api/batches/1/summary/ \
  -H "Authorization: Bearer <access_token>"
```

### Get Institution Summary (Programme Manager)
```bash
curl -X GET http://localhost:8000/api/institutions/1/summary/ \
  -H "Authorization: Bearer <access_token>"
```

### Get Programme Summary (Programme Manager)
```bash
curl -X GET http://localhost:8000/api/programme/summary/ \
  -H "Authorization: Bearer <access_token>"
```

### Get Monitoring Attendance (Monitoring Officer with scoped token)
```bash
curl -X GET http://localhost:8000/api/monitoring/attendance/ \
  -H "Authorization: Bearer <scoped_access_token>"
```

## Schema Decisions

- **Users**: Custom User model with roles and institution relationship. Passwords are hashed using Django's set_password.
- **Batches**: Belong to institutions, with many-to-many relationships for trainers and students.
- **Batch Invites**: UUID tokens for joining batches, with expiration.
- **Sessions**: Tied to batches and trainers, with attendance records.
- **Attendance**: Status choices (present, absent, late), unique per session-student.
- **Dual-token approach for Monitoring Officer**: Standard JWT for login, short-lived scoped token for monitoring access to prevent misuse.

## What is Fully Working

- User authentication and signup with JWT.
- Role-based access control on all endpoints.
- CRUD operations for batches, sessions, and attendance.
- Batch invite and join functionality.
- Summary endpoints with attendance statistics.
- Monitoring officer special access with scoped tokens.
- Basic validation and error handling.

## What is Partially Done

- Some edge cases in permission checks may need refinement.
- Deployment to production not implemented (only local).
- Full deployment to Render.


