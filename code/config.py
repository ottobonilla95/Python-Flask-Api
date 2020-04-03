import os

# basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_ECHO = False
SQLALCHEMY_TRACK_MODIFICATIONS = True
SQLALCHEMY_DATABASE_URI = "postgresql://devuser:Q.654321o@128.199.43.48:5432/storeapp-db"
PROPAGATE_EXCEPTIONS = True
DEBUG= True
JWT_SECRET_KEY = 'super-secret'

