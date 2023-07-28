import logging
import secrets
import os

from dotenv import load_dotenv, find_dotenv

basedir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(find_dotenv())


class Config():
    """Set Flask configuration vars from .env file."""
    
    # General Config
    SECRET_KEY = os.environ.get('SECRET_KEY')
    FLASK_APP = os.environ.get('FLASK_APP')
    FLASK_ENV = os.environ.get('FLASK_ENV')
    
    # Database
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")