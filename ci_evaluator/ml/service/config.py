import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='.flaskenv', verbose=True)


class Config:
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', '')
