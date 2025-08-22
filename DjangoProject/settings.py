"""
Django settings for DjangoProject project.
"""

from pathlib import Path
import environ

# -----------------------------
# BASE DIR
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# ENVIRONMENT
# -----------------------------
env = environ.Env(
    DEBUG=(bool, False)
)

# citim fișierul .env din rădăcina proiectului (lângă manage.py)
environ.Env.read_env(BASE_DIR / ".env")

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = env("SECRET_KEY")
DEBUG = env("DEBUG", default=True)
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

# -----------------------------
# EMAIL
# -----------------------------
EMAIL_BACKEND = env("EMAIL_BACKEND")
EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")

# -----------------------------
# INSTALLED APPS
# -----------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",

    # Third-party
    "rest_framework",
    "rest_framework_simplejwt",
    "drf_spectacular",
    "django_filters",
    "django_minio_backend",
    "django_elasticsearch_dsl",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.github",

    # Local apps
    "apps.tasks",
    "apps.users",
]

SITE_ID = 1

# -----------------------------
# MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "DjangoProject.urls"

# -----------------------------
# TEMPLATES
# -----------------------------
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
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

WSGI_APPLICATION = "DjangoProject.wsgi.application"

# -----------------------------
# DATABASE
# -----------------------------
DATABASES = {
    "default": {
        "ENGINE": env("DB_ENGINE"),
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASSWORD"),
        "HOST": env("DB_HOST"),
        "PORT": env("DB_PORT"),
    }
}

# -----------------------------
# CACHES
# -----------------------------
CACHES = {
    "default": {
        "BACKEND": env("CACHE_BACKEND"),
        "LOCATION": env("CACHE_LOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": env("CACHE_CLIENT_CLASS", default="django_redis.client.DefaultClient"),
        },
    }
}

# -----------------------------
# AUTHENTICATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

SOCIALACCOUNT_PROVIDERS = {
    "github": {
        "APP": {
            "client_id": env("GITHUB_CLIENT_ID"),
            "secret": env("GITHUB_SECRET"),
            "key": env("GITHUB_KEY"),
        }
    }
}

LOGIN_REDIRECT_URL = "/accounts/profile/"

# -----------------------------
# REST FRAMEWORK
# -----------------------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Task Managment System API",
    "DESCRIPTION": "A simple API for managing tasks and users",
    "VERSION": "1.0.0",
}

# -----------------------------
# ELASTICSEARCH
# -----------------------------
ELASTICSEARCH_DSL = {
    "default": {"hosts": env("ELASTICSEARCH_HOST")},
}

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "django.core.files.storage.FileSystemStorage"

# -----------------------------
# MEDIA FILES (MinIO)
# -----------------------------
STORAGES = {
    "default": {
        "BACKEND": "django_minio_backend.models.MinioBackend",
        "OPTIONS": {
            "bucket_name": "my-media-bucket",
            "auto_create_bucket": True,
        },
    },
    "staticfiles": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": BASE_DIR / "staticfiles",
        },
    },
}
DEFAULT_FILE_STORAGE = "django_minio_backend.models.MinioBackend"

MINIO_ENDPOINT = env("MINIO_ENDPOINT")
MINIO_ACCESS_KEY = env("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = env("MINIO_SECRET_KEY")
MINIO_USE_HTTPS = env("MINIO_USE_HTTPS", default=False)
MINIO_PUBLIC_BUCKETS = env.list("MINIO_PUBLIC_BUCKETS")
MINIO_CONSISTENCY_CHECK_ON_START = env.bool(
    "MINIO_CONSISTENCY_CHECK_ON_START", default=False
)

# -----------------------------
# CELERY
# -----------------------------
CELERY_BROKER_URL = env("CELERY_BROKER_URL")
CELERY_TIMEZONE = env("CELERY_TIMEZONE")
CELERY_TASK_TRACK_STARTED = env.bool("CELERY_TASK_TRACK_STARTED", default=True)
CELERY_TASK_TIME_LIMIT = env.int("CELERY_TASK_TIME_LIMIT", default=30 * 60)
CELERY_RESULT_BACKEND = env("CELERY_RESULT_BACKEND")
CELERY_TASKS_ALWAYS_EAGER = env.bool("CELERY_TASKS_ALWAYS_EAGER", default=True)

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -----------------------------
# DEFAULT PK FIELD
# -----------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
