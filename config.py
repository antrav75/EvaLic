import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'clavesecreta')
    DATABASE = os.environ.get('DATABASE', os.path.join(BASE_DIR, 'db_EvaLic.db'))
