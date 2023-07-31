import logging
import secrets
import os

from dotenv import load_dotenv, find_dotenv

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(find_dotenv())


class Config():
    """Set Flask configuration vars from .env file."""
    
    ENV = os.environ.get('ENV')
    
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_APP = "app.py"
    
    if ENV == 'dev':
        SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    else:
        HEROKU_DB_URL = os.environ.get("DATABASE_URL")
        SQLALCHEMY_DATABASE_URI = HEROKU_DB_URL.replace("postgres://", "postgresql://")
