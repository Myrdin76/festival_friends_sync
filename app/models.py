from datetime import datetime, timedelta
from time import time
import jwt

import uuid

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.dialects.postgresql import UUID

from app import app, db, lm, config

class User(UserMixin, db.Model):
    """Data model for user accounts"""
    
    # columns
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = db.Column(db.String(80))
    password_hash = db.Column(db.String(128))
    email = db.Column(db.String(80), nullable=False)
    created = db.Column(db.DateTime, default=datetime.now())
    admin = db.Column(db.Boolean, nullable=False, default=False)
    department = db.Column(db.String(80), nullable=True, default=False)
    
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_reset_password_token(self, expires_in=3600*72):
        return jwt.encode(
            {'reset_password': str(self.id), 'exp': time() + expires_in},
            config.SECRET_KEY, algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, config.SECRET_KEY,
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return "<User {}>".format(self.username)

@lm.user_loader
def load_user(id):
    return User.query.get(id)
