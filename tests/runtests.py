import django
import os
import sys

from django.conf import settings

DIRNAME = os.path.dirname(__file__)
PARENT_DIR = os.path.dirname(os.path.abspath(DIRNAME))

sys.path.insert(1, PARENT_DIR)

settings.configure(
    DEBUG = True,
    ROOT_URLCONF='urls',
    DATABASES={
        "default": {
            "ENGINE": 'django.db.backends.sqlite3',
        }
    },
    TEMPLATES=[
        {
            "BACKEND": "django.template.backends.django.DjangoTemplates",
            'OPTIONS': {
                'context_processors': [
                    # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                    # list if you haven't customized them:
                    'django.contrib.auth.context_processors.auth',
                    'django.template.context_processors.debug',
                    'django.template.context_processors.i18n',
                    'django.template.context_processors.media',
                    'django.template.context_processors.static',
                    'django.template.context_processors.tz',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ],
    INSTALLED_APPS = (
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.admin',
        'megamacros',
    )
)


django.setup()
from django.test.runner import DiscoverRunner
test_runner = DiscoverRunner(verbosity=1)

failures = test_runner.run_tests(['megamacros'])
if failures:
    sys.exit(failures)