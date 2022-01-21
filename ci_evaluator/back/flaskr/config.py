import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.flaskenv', verbose=True)


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite://')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    ML_SERVICE_URI = os.getenv('SERVICE_URL', '')
