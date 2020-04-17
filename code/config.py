import os
import datetime

# DEBUG
PROPAGATE_EXCEPTIONS = True
DEBUG = True

# sql alchemy
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI")

# JWT
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')


# Babel
SUPPORTED_LANGUAGES = {'en': 'English',
                       'es': 'Spanish'}

BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
