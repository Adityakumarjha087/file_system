# Secure File Sharing System with Django REST Framework

A secure file sharing system with role-based access control built with Django and Django REST Framework.

## Features

- JWT-based authentication
- Role-based access control (Ops and Client roles)
- Secure file upload and download
- File type validation (.docx, .pptx, .xlsx)
- Secure download links with expiration
- RESTful API endpoints

## Prerequisites

- Python 3.8+
- pip

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd django
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run migrations:
   ```bash
   python manage.py migrate
   ```

5. Create a superuser (admin):
   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## API Endpoints

### Authentication
- `POST /api/signup/` - Register a new user
- `POST /api/login/` - Obtain JWT tokens
- `POST /api/token/refresh/` - Refresh access token

### File Operations (Ops only)
- `POST /api/upload/` - Upload a new file

### File Operations (Clients only)
- `GET /api/files/` - List all uploaded files
- `GET /api/download/<token>/` - Download a file using a secure token

## Usage

1. Register a new user with a role (ops/client)
2. Log in to get your access token
3. Use the access token in the Authorization header: `Bearer <token>`
4. Access the appropriate endpoints based on your role

## Security

- All API endpoints require authentication
- File uploads are restricted to specific file types
- Download links expire after 1 hour
- Sensitive data is not stored in plain text

## License

This project is licensed under the MIT License.
