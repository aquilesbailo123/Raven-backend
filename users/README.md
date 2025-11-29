# Users App

## Purpose

The Users app handles all aspects of user management, authentication, and security in the Daddy Django project. It provides a comprehensive authentication system that extends Django's default capabilities with additional security features and user profile management.

## Features

- **Authentication System**: Built on dj-rest-auth and allauth with customizations
- **User Profile**: Extended user model with additional information and security settings
- **Login History**: Tracking of login attempts with IP and device information
- **Security Features**: 
  - Action freezing for suspicious activities
  - IP change detection with notifications
  - Captcha integration for sensitive operations
  - Email verification workflows
- **REST API Endpoints**: Authentication-related API endpoints with proper serializers
- **Custom Adapters**: Adapters for third-party authentication services
- **Password Management**: Secure password reset and change workflows

## Structure

```
users/
├── auth/                # Authentication-related components
│   ├── adapters.py      # Adapters for authentication services
│   └── backends.py      # Custom authentication backends
├── migrations/          # Database migrations
├── serializers/         # API serializers
│   ├── auth.py          # Authentication serializers
│   └── profile.py       # User profile serializers
├── admin.py             # Admin site registrations
├── apps.py              # App configuration
├── cache_keys.py        # Cache key definitions
├── captcha.py           # Captcha handling
├── exceptions.py        # Custom exceptions
├── models.py            # User-related models
├── signals.py           # Signal handlers
├── tasks.py             # Asynchronous tasks
├── urls.py              # URL configurations
├── utils.py             # Utility functions
└── views.py             # Authentication views
```

## Key Components

### Models

- **Profile**: Extends the User model with additional fields and security methods
  - `user_type`: User type ('startup' or 'incubator')
  - `actions_freezed_till`: Security feature for freezing user actions
- **Startup**: Company information for startup users
  - `profile`: OneToOne relationship with Profile (user_type must be 'startup')
  - `company_name`: Company name
  - `industry`: Industry classification
  - `logo_url`: URL to company logo in Google Cloud Storage
  - `is_mock_data`: Indicates if this is sample/mock data
- **LoginHistory**: Records login attempts with context information

### Authentication Flow

1. User registration with email verification
2. Login with security checks (IP tracking, captcha)
3. Password management (reset, change) with security measures
4. Optional two-factor authentication infrastructure

### Security Measures

- IP change detection sends notifications to users
- Account action freezing after sensitive operations
- Login history tracking for security auditing
- Captcha validation for sensitive operations

## Extending

When extending the Users app:

1. Use the existing authentication flow as much as possible
2. Extend the Profile model for additional user information
3. Add new serializers in the appropriate directory
4. Implement additional security measures as needed

## Integration

The Users app is designed to be the central authentication system for the entire project. New apps should:

1. Use the Profile model for user-related information
2. Leverage the authentication system for securing endpoints
3. Follow the established security patterns

## User Types

The system implements two different types of users:

- **startup**: Usuario tipo Startup (emprendimiento)
- **incubadora**: Usuario tipo Incubadora

The user type is stored in the `Profile` model and must be specified during registration.

## URLs & Endpoints

### Authentication Base

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/auth/login/` | POST | User login | No |
| `/auth/logout/` | POST | User logout | Yes |
| `/auth/user/` | GET | Get current user data | Yes |
| `/auth/password/change/` | POST | Change password | Yes |
| `/auth/password/reset/` | POST | Request password reset | No |

### Registration

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/auth/registration/` | POST | Register new user | No |
| `/auth/registration/account-confirm-email/` | POST | Confirm email with code | No |
| `/resend-email-confirmation/` | POST | Resend confirmation email | No |

### Password Reset

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/reset-password/<uidb64>/<token>/` | GET | Password reset view | No |

### Onboarding

| URL | Method | Description | Auth Required |
|-----|--------|-------------|---------------|
| `/onboarding/startup/` | GET | Get startup information and onboarding status | Yes (startup only) |
| `/onboarding/startup/` | POST | Complete startup onboarding | Yes (startup only) |

## API Request/Response Examples

### POST `/auth/registration/` - Register

**Request Body:**
```json
{
  "email": "user@example.com",
  "password1": "secure_password",
  "password2": "secure_password",
  "user_type": "startup",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Required Fields:**
- `email`: User email
- `password1`: Password
- `password2`: Password confirmation
- `user_type`: User type - must be `"startup"` or `"incubadora"`

**Optional Fields:**
- `first_name`: First name
- `last_name`: Last name

**Response (201 Created):**
```json
{
  "detail": "Verification e-mail sent."
}
```

### POST `/auth/login/` - Login

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "secure_password"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "user": {
    "username": "generated_username",
    "email": "user@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "is_staff": false,
    "user_type": "startup",
    "onboarding_complete": false,
    "company_name": null,
    "actions_freezed_till": null
  }
}
```

**JWT Tokens:**
- `access_token`: Access token (valid for 1 day)
- `refresh_token`: Refresh token (valid for 5 days)

### GET `/auth/user/` - Get Current User

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "username": "generated_username",
  "email": "user@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "is_staff": false,
  "user_type": "startup",
  "onboarding_complete": false,
  "company_name": null,
  "actions_freezed_till": null
}
```

### POST `/onboarding/startup/` - Complete Startup Onboarding

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "company_name": "My Startup Inc.",
  "industry": "saas"
}
```

**Required Fields:**
- `company_name`: Company name (string)
- `industry`: Industry type (string) - Valid options: `technology`, `fintech`, `healthtech`, `edtech`, `ecommerce`, `saas`, `ai_ml`, `blockchain`, `marketplace`, `other`

**Response (200 OK):**
```json
{
  "detail": "Onboarding completed successfully.",
  "startup": {
    "id": 1,
    "company_name": "My Startup Inc.",
    "industry": "saas",
    "logo_url": null,
    "is_mock_data": true,
    "created": "2025-11-29T12:00:00Z",
    "updated": "2025-11-29T12:00:00Z"
  },
  "is_onboarding_complete": true
}
```

**Error Response (403 Forbidden - Not a startup user):**
```json
{
  "detail": "This endpoint is only for startup users."
}
```

**Error Response (400 Bad Request - Validation error):**
```json
{
  "company_name": ["Company name cannot be empty"],
  "industry": ["Industry must be selected"]
}
```

### GET `/onboarding/startup/` - Get Startup Onboarding Status

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "startup": {
    "id": 1,
    "company_name": "My Startup Inc.",
    "industry": "saas",
    "logo_url": null,
    "is_mock_data": true,
    "created": "2025-11-29T12:00:00Z",
    "updated": "2025-11-29T12:00:00Z"
  },
  "is_onboarding_complete": true
}
```

## Frontend Integration

### Configure Axios for JWT

```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://127.0.0.1:8000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true
});

// Add token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Handle token expiration
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post('http://127.0.0.1:8000/auth/token/refresh/', {
          refresh: refreshToken
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

export default api;
```

### Registration Example

```javascript
import api from './api';

async function register(userData) {
  const response = await api.post('/auth/registration/', {
    email: userData.email,
    password1: userData.password,
    password2: userData.password,
    user_type: userData.userType, // "startup" or "incubadora"
    first_name: userData.firstName,
    last_name: userData.lastName
  });
  return response.data;
}
```

### Login Example

```javascript
import api from './api';

async function login(email, password) {
  const response = await api.post('/auth/login/', { email, password });
  const { access_token, refresh_token, user } = response.data;

  localStorage.setItem('access_token', access_token);
  localStorage.setItem('refresh_token', refresh_token);
  localStorage.setItem('user', JSON.stringify(user));

  return user;
}
```

### Protected Routes in React

```javascript
import { Navigate } from 'react-router-dom';

function ProtectedRoute({ children }) {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
}
```

## Database Administration

### Direct PostgreSQL Connection (Neon)

**Connection details:**
- Host: `ep-orange-mode-ahlvekcr-pooler.c-3.us-east-1.aws.neon.tech`
- Port: `5432`
- Database: `neondb`
- User: `neondb_owner`
- Password: See `.env` file

### Using Django Shell

```bash
source venv/bin/activate
python manage.py shell

from django.contrib.auth import get_user_model
from users.models import Profile

User = get_user_model()

# Query all users
users = User.objects.all()
for user in users:
    print(f"Email: {user.email}, Type: {user.profile.user_type}")

# Query by user type
startups = Profile.objects.filter(user_type='startup')
incubadoras = Profile.objects.filter(user_type='incubadora')

# Change user type
profile = Profile.objects.get(user__email='user@example.com')
profile.user_type = 'incubadora'
profile.save()
```

### Using psql (Terminal)

```bash
psql "postgresql://neondb_owner:npg_9ASj1eiEnOqb@ep-orange-mode-ahlvekcr-pooler.c-3.us-east-1.aws.neon.tech:5432/neondb?sslmode=require"

# Useful queries
SELECT * FROM users_profile;
SELECT u.email, p.user_type FROM auth_user u JOIN users_profile p ON u.id = p.user_id;
SELECT user_type, COUNT(*) FROM users_profile GROUP BY user_type;

# Update user type
UPDATE users_profile SET user_type = 'incubadora' WHERE user_id = (SELECT id FROM auth_user WHERE email = 'user@example.com');
```

### Using GUI Tools (DBeaver/pgAdmin/TablePlus)

1. Create new PostgreSQL connection
2. Configure:
   - Host: `ep-orange-mode-ahlvekcr-pooler.c-3.us-east-1.aws.neon.tech`
   - Port: `5432`
   - Database: `neondb`
   - Username: `neondb_owner`
   - Password: (from .env file)
   - SSL Mode: `require`

### Management Commands

```bash
source venv/bin/activate

# Create superuser
python manage.py createsuperuser

# Access Django admin
# http://127.0.0.1:8000/admin/

# Database shell
python manage.py dbshell

# Run migrations
python manage.py migrate

# Create migrations
python manage.py makemigrations

# View migration SQL
python manage.py sqlmigrate users 0002
```

### Backup and Restore

```bash
# Backup database
pg_dump "postgresql://neondb_owner:npg_9ASj1eiEnOqb@ep-orange-mode-ahlvekcr-pooler.c-3.us-east-1.aws.neon.tech:5432/neondb?sslmode=require" > backup.sql

# Restore database
psql "postgresql://neondb_owner:npg_9ASj1eiEnOqb@ep-orange-mode-ahlvekcr-pooler.c-3.us-east-1.aws.neon.tech:5432/neondb?sslmode=require" < backup.sql
```

## Security Configuration

### JWT Settings

- **Access Token Lifetime**: 1 day
- **Refresh Token Lifetime**: 5 days
- **Algorithm**: HS512
- **Auto Rotate**: Yes (generates new refresh token on each use)

### Email Verification

- Email verification is **mandatory** by default
- Users must confirm their email before logging in
- Verification codes expire after 1 day

### Rate Limiting

- API throttling configured:
  - Anonymous users: 5 requests/second
  - Authenticated users: 10 requests/second

## Troubleshooting

### "Email not verified"
- User needs to verify email first
- Use `/resend-email-confirmation/` endpoint with provided token

### "Invalid token"
- JWT token has expired
- Use refresh token to get new access token
- POST to `/auth/token/refresh/` with `{"refresh": "token"}`

### CORS errors
- Verify frontend domain is in `CORS_ALLOWED_ORIGINS`
- Verify `withCredentials: true` is configured in axios
