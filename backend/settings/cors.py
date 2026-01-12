from .env import env

# CORS Configuration
# NOTE adjust this for production
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173",
    f"https://{env('FRONTEND_DOMAIN', default='localhost:3000')}",
    "https://raven-frontend.vercel.app",
    "https://www.raven-frontend.vercel.app",
    f"https://{env('DOMAIN', default='localhost')}",
]

# Allow credentials to be included in CORS requests (for JWT cookies if needed)
CORS_ALLOW_CREDENTIALS = True

# Allow common headers for JWT authentication
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]