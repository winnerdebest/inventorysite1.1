from pathlib import Path
import os
import dj_database_url
import cloudinary
import cloudinary.uploader
import cloudinary.api
from cloudinary.utils import cloudinary_url




from environ import Env
env = Env()
Env.read_env()
ENVIRONMENT = env('ENVIRONMENT', default='production')
USE_CLOUDINARY = env.bool('USE_CLOUDINARY', default=False)



# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
if ENVIRONMENT == 'development':
    DEBUG = True
else:
    DEBUG = False

ALLOWED_HOSTS = ['localhost', '127.0.0.1', 'inventorysite.onrender.com',]


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'main',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventorysite.urls'

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

WSGI_APPLICATION = 'inventorysite.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Fix the images 
# Fix the Oil and Gas Section

POSTGRESS_LOCALLY = True
if ENVIRONMENT == 'production' or POSTGRESS_LOCALLY == True:
        DATABASES['default'] = dj_database_url.parse(env('DATABASE_URL'))


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True




# Cloudinary Settings

if ENVIRONMENT == 'production' or USE_CLOUDINARY:
    # Cloudinary configuration
    CLOUDINARY = {
        'cloud_name': env('CLOUDINARY_CLOUD_NAME'),
        'api_key': env('CLOUDINARY_API_KEY'),
        'api_secret': env('CLOUDINARY_API_SECRET'),
    }

    cloudinary.config(**CLOUDINARY)

    # Media URL for Cloudinary
    MEDIA_URL = f"https://res.cloudinary.com/{CLOUDINARY['cloud_name']}/"
else:
    # Local media setup
    MEDIA_URL = '/media/'
    MEDIA_ROOT = BASE_DIR / 'media'



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')#STATIC_ROOT = '/var/www/static'
STATIC_URL = 'static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static')
]


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'