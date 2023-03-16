from . import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'home_credit_api',
        'USER': 'postgres',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '5433',  # psql 13 will run on this port on travis
    },
}
