"""
Django settings for DjangoProject project.
"""

from pathlib import Path

# -----------------------------
# BASE DIR
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------
# SECURITY
# -----------------------------
SECRET_KEY = 'django-insecure-padp=i%lys6-s3-+%vwbja9rxsu$=7undv(8txc$b^j90h)=ta'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'host.docker.internal']

# -----------------------------
# EMAIL
# -----------------------------
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025

# -----------------------------
# INSTALLED APPS
# -----------------------------
INSTALLED_APPS = [
    # Django
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Third-party
    'rest_framework',
    'rest_framework_simplejwt',
    'drf_spectacular',
    'django_filters',
    'django_minio_backend',
    'django_elasticsearch_dsl',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.github',

    # Local apps
    'apps.tasks',
    'apps.users',
]

SITE_ID = 1

# -----------------------------
# MIDDLEWARE
# -----------------------------
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

ROOT_URLCONF = 'DjangoProject.urls'

# -----------------------------
# TEMPLATES
# -----------------------------
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'DjangoProject.wsgi.application'

# -----------------------------
# DATABASE
# -----------------------------
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'django-db',
        'USER': 'django-user',
        'PASSWORD': 'passw0rd',
        'HOST': 'db',
        'PORT': '5432',
    }
}

# -----------------------------
# CACHES
# -----------------------------
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/1",
        "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient"},
    }
}

# -----------------------------
# AUTHENTICATION
# -----------------------------
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

SOCIALACCOUNT_PROVIDERS = {
    'github': {
        'APP': {
            'client_id': 'Ov23lia487wKwwf5GLlE',
            'secret': '88bc004e9b0bb5c5499580f8e9a68565b0345d23',
            'key': ''
        }
    }
}

LOGIN_REDIRECT_URL = '/accounts/profile/'

# -----------------------------
# REST FRAMEWORK
# -----------------------------
REST_FRAMEWORK = {
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_FILTER_BACKENDS': (
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.OrderingFilter',
        'rest_framework.filters.SearchFilter',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'Task Managment System API',
    'DESCRIPTION': 'A simple API for managing tasks and users',
    'VERSION': '1.0.0',
}

# -----------------------------
# ELASTICSEARCH
# -----------------------------
ELASTICSEARCH_DSL = {
    'default': {'hosts': 'http://elasticsearch:9200'}
}

# -----------------------------
# STATIC FILES
# -----------------------------
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'django.core.files.storage.FileSystemStorage'

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

MINIO_ENDPOINT = 'minio:9000'
MINIO_ACCESS_KEY = 'minio_user'
MINIO_SECRET_KEY = 'minio_password'
MINIO_USE_HTTPS = False
MINIO_PUBLIC_BUCKETS = ['django-backend-dev-public']
MINIO_CONSISTENCY_CHECK_ON_START = False

# -----------------------------
# CELERY
# -----------------------------
CELERY_BROKER_URL = 'amqp://rabbit_user:rabbit_password@rabbitmq:5672//'
CELERY_TIMEZONE = "Europe/Chisinau"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_BACKEND = "redis://redis:6379/2"
CELERY_TASKS_ALWAYS_EAGER = True

# -----------------------------
# INTERNATIONALIZATION
# -----------------------------
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# -----------------------------
# DEFAULT PK FIELD
# -----------------------------
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
