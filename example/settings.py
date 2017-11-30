from os.path import abspath, dirname, join, pardir

PROJECT_DIR = abspath(join(dirname(__file__), pardir))

SECRET_KEY = '=n@i1l$4yh+o%h26g8%8li=6huwmr3h4y=28mpnk3-fu8=_^7s'
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': join(PROJECT_DIR, '.local_db'),
    }
}

PROJECT_APPS = ('viewattrs', )

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django_nose',
) + PROJECT_APPS

TEST_RUNNER = 'django_nose.NoseTestSuiteRunner'
