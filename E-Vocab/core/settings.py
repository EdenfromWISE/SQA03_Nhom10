

from pathlib import Path
import environ

# Initialize environment
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env()
environ.Env.read_env(str(BASE_DIR / ".env"))

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# (Moved BASE_DIR above for env initialization)


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ['*'] 


# Application definition

INSTALLED_APPS = [
    # Django apps
    "whitenoise.runserver_nostatic",  # WhiteNoise for static files (must be before staticfiles)
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",  # Cần cho allauth
    "import_export",
    # Third-party apps
    "corsheaders",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "dj_rest_auth",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "solo",
    # Your apps
    "chatbot",
    "vocabulary",
    "students",
    "progress",
    "learning",
]

SITE_ID = 1

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # WhiteNoise for static files
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"

# Cấu hình MySQL
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME", default="django_vocab"),
        "USER": env("DB_USER", default="root"),
        "PASSWORD": env("DB_PASSWORD", default="123456"),
        "HOST": env("DB_HOST", default="localhost"),
        "PORT": env("DB_PORT", default="3306"),
        "OPTIONS": {
            "init_command": "SET sql_mode='STRICT_TRANS_TABLES', character_set_connection=utf8mb4, collation_connection=utf8mb4_unicode_ci",
            "charset": "utf8mb4",
        },
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = env("LANGUAGE_CODE", default="en-us")

TIME_ZONE = env("TIME_ZONE", default="Asia/Ho_Chi_Minh")

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# WhiteNoise configuration for serving static files
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
}

from datetime import timedelta

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
}

CORS_ALLOW_ALL_ORIGINS = False
# Cho phép gửi cookie qua CORS (cần cho session)
CORS_ALLOW_CREDENTIALS = True

# CORS_ALLOWED_ORIGINS = env.list(
#     "CORS_ALLOWED_ORIGINS",
#     default=["http://localhost:5173", "http://127.0.0.1:5173", "https://fe-e-vocab.vercel.app"],
# )
CORS_ALLOWED_ORIGINS = [
    "https://fe-e-vocab.vercel.app", # Frontend Production
    "http://localhost:5173",         # Frontend Dev
]
# CSRF_TRUSTED_ORIGINS = env.list(
#     "CSRF_TRUSTED_ORIGINS",
#     default=[
#         "https://e-vocab-production.up.railway.app",
#         "https://fe-e-vocab.vercel.app",  # Frontend URL
#     ]
# )
CORS_ALLOW_CREDENTIALS = True

# 4. Các cấu hình phụ trợ
CORS_ALLOW_HEADERS = ["*"]
CORS_ALLOW_METHODS = ["*"]

# 5. Cấu hình Cookie (Vì Frontend và Backend khác domain nên phải là None)
SESSION_COOKIE_SAMESITE = 'None'
CSRF_COOKIE_SAMESITE = 'None'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# 6. Trust Origin
CSRF_TRUSTED_ORIGINS = [
    "https://e-vocab-production.up.railway.app",
    "https://fe-e-vocab.vercel.app",
]

# 7. Giữ cái này để không bị chặn Popup Google
SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

# CORS headers và methods
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

CORS_ALLOW_METHODS = [
    'DELETE',
    'GET',
    'OPTIONS',
    'PATCH',
    'POST',
    'PUT',
]
# SECURE_CROSS_ORIGIN_OPENER_POLICY = 'same-origin-allow-popups'

SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'
# Railway deployment settings
# Security settings cho production
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTHENTICATION_BACKENDS = [
    # Needed to login by username in Django admin, regardless of `allauth`
    "django.contrib.auth.backends.ModelBackend",
    # `allauth` specific authentication methods, such as login by e-mail
    "allauth.account.auth_backends.AuthenticationBackend",
]

# Django-allauth settings
ACCOUNT_EMAIL_VERIFICATION = "none"
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_USERNAME_REQUIRED = False  # Chúng ta sẽ dùng email làm định danh chính


# Google provider settings
SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "SCOPE": [
            "profile",
            "email",
        ],
        "AUTH_PARAMS": {
            "access_type": "offline",
        },
        "OAUTH_PKCE_ENABLED": True,
        "APP": {
            "client_id": env("GOOGLE_CLIENT_ID", default=""),
            "secret": env("GOOGLE_CLIENT_SECRET", default=""),
            "key": "",
        },
    }
}
# SOCIALACCOUNT_PROVIDERS = {
#     'google': {
#         # For each provider, you can choose whether to request 'profile', 'email', or both.
#         'SCOPE': [
#             'profile',
#             'email',
#         ],
#         # Auth parameters for Google OAuth2
#         'AUTH_PARAMS': {
#             'access_type': 'offline',
#         },
#         # Client ID and secret for the Google app
#         'APP': {
#             'client_id': 'YOUR_GOOGLE_CLIENT_ID', # <-- THAY CLIENT ID CỦA BẠN
#             'secret': 'YOUR_GOOGLE_CLIENT_SECRET', # <-- THAY CLIENT SECRET
#             'key': '' # Để trống
#         }
#     }
# }

REST_AUTH = {
    "USE_JWT": True,
    "JWT_AUTH_HTTPONLY": False,  # Cho phép JS phía client truy cập token
}

# Frontend base URL for password reset links in dev
FRONTEND_BASE_URL = env("FRONTEND_BASE_URL", default="http://localhost:5173")

# Redis Cache Configuration
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
