<div align="center">
  <img src="static/images/chadicon.svg" alt="Daddy Django Logo" width="120" height="120">
</div>

# Daddy Django

A comprehensive Django template designed for building scalable and secure backend applications.

## Overview

Daddy Django is a robust Django project template that provides a solid foundation for building production-ready backend applications. It includes a comprehensive authentication system, modular settings, and follows Django best practices.

## Key Features

- **Modular Settings**: Split configuration into specialized modules for different aspects
- **Comprehensive Authentication**: Secure user authentication with dj-rest-auth and allauth ([see AUTH_ENDPOINTS.md](AUTH_ENDPOINTS.md))
- **Security Features**: OTP for admin, IP tracking, action freezing, captcha integration
- **REST API Ready**: Set up with Django REST framework and appropriate serializers
- **Background Processing**: Celery integration for asynchronous tasks
- **Caching**: Redis-based caching infrastructure
- **Email Templates**: Professional email templates with modern design
- **Internationalization**: Support for multiple languages

## Project Structure

```
daddy-django/
├── backend/               # Main Django configuration
│   ├── settings/          # Modular settings files
│   └── ...
├── build_scripts/         # Deployment scripts
├── core/                  # Core functionality and shared components
├── users/                 # User management and authentication
├── utils/                 # Utility functions and helpers
└── static/                # Static files
```

## Apps

- **core**: Houses shared templates, templatetags, and base functionality
- **users**: Comprehensive authentication system with profile management
- **utils**: Reusable functions and helpers across the project

## Getting Started

1. Clone the repository
2. Copy `.env.template` to `.env` and set your environment variables
3. Install dependencies: `pip install -r requirements.txt`
4. Run migrations: `python manage.py migrate`
5. Create a superuser: `python manage.py createsuperuser`
6. Run the server: `python manage.py runserver`

## Deployment

Use the provided build script for deployment:

```bash
./build_scripts/render.sh
```

## Management Scripts

### Delete Non-Admin Users
To delete all users except superusers and staff (useful for cleaning up test data):

```bash
python delete_non_admin_users.py
```

## Extending the Project

This template is designed to be extended. When adding new functionality:

1. Create a new Django app if needed: `python manage.py startapp app_name`
2. Follow the established patterns for models, views, and serializers
3. Update the settings as needed
4. Register the app in `INSTALLED_APPS` in settings

## License

This project is freely available for use without restrictions. Anyone who clones this repository is welcome to use, modify, and distribute it as they see fit. No attribution required.
