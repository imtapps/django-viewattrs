from os.path import abspath, dirname, join, pardir

PROJECT_DIR = abspath(join(dirname(__file__), pardir))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_DIR, '.local_db'),
        }
}

PROJECT_APPS = (
    'viewattrs',
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_nose',
) + PROJECT_APPS

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
