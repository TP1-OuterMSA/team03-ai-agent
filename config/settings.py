from pathlib import Path
from django.core.exceptions import ImproperlyConfigured
import json
import pymysql
import os
pymysql.install_as_MySQLdb()

BASE_DIR = Path(__file__).resolve().parent.parent

secret_file = BASE_DIR / "secrets.json"
with open(secret_file) as file:
    secrets = json.loads(file.read())
def get_secrets(setting, secrets_dict=secrets):
    try:
        return secrets_dict[setting]
    except KeyError:
        error_msg = f'set the {setting} environment variable'
        raise ImproperlyConfigured(error_msg)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = get_secrets('SECRET')
OPENAI_API = get_secrets("OPENAIAPI")

DEBUG = True
ALLOWED_HOSTS = ['*']
CORS_ALLOW_ALL_ORIGINS = True
# CORS_ALLOWED_ORIGINS = ['*']

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    "llmchatbot",
    'drf_yasg',
]

### swagger
is_kubernetes = os.environ.get('KUBERNETES_SERVICE_HOST') is not None

if is_kubernetes:
    STATIC_URL = '/api/team3/llmchatbot/static/'
else:
    STATIC_URL = '/static/'

SWAGGER_SETTINGS = {
    'USE_SESSION_AUTH': False,
    'SECURITY_DEFINITIONS': None,
    'LOGIN_URL': None,
    'LOGOUT_URL': None,
    'SWAGGER_UI_DIST': 'https://unpkg.com/swagger-ui-dist@3.52.5',
    'VALIDATOR_URL': None,
    'USE_LOCAL_FILES': False,
}

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ],
}
###

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    'whitenoise.middleware.WhiteNoiseMiddleware',
]
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        'DIRS': [BASE_DIR / 'templates'],
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

WSGI_APPLICATION = "config.wsgi.application"


# Database
DATABASES = {
    'default': {
        'ENGINE': get_secrets('ENGINE'),
        'NAME': get_secrets('NAME'),
        'USER': get_secrets('USER'),
        'PASSWORD': get_secrets('PASSWORD'),
        'HOST': get_secrets('HOST'),
        'PORT': get_secrets('PORT'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

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
# Internationalization
LANGUAGE_CODE = 'ko-kr'
TIME_ZONE = 'Asia/Seoul'
USE_I18N = True
USE_TZ = False
TIME_ZONE = 'Asia/Seoul'
# Static files (CSS, JavaScript, Images)
# STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
# AUTH_USER_MODEL = 'users.User'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}