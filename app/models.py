from datetime import datetime, timedelta
from time import time
import jwt

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time

from app import db, lm, config


user_to_group = db.Table(
    "user_to_group",
    db.metadata,
    Column("user_id", Integer, ForeignKey("user.user_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("group.group_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
)

user_to_artist = db.Table(
    "user_to_artist",
    db.metadata,
    Column("user_id", Integer, ForeignKey("user.user_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
    Column("artist_id", Integer, ForeignKey("artist.artist_id", onupdate="CASCADE", ondelete="CASCADE"), primary_key=True),
)


class User(UserMixin, db.Model):
    """Data model for user accounts"""
    
    __tablename__ = "user"

    # columns
    user_id = Column(Integer, autoincrement=True, primary_key=True)
    username = Column(String(80), nullable=False, unique=True)
    password_hash = Column(String(128))
    email = Column(String(80), nullable=True)
    created = Column(DateTime, default=datetime.now())

    groups = db.relationship("Group", secondary=user_to_group, backref="group")
    artists = db.relationship("Artist", secondary=user_to_artist, backref="artist")
    
    def get_all_artists_ordered(self):
        res = db.session.query(Artist).filter(Artist.artist_id.in_([art.artist_id for art in self.artists])).order_by(Artist.startdate).all()
        return res
    
    def get_friends(self, group_id):
        friends = db.session.query(User).filter(User.user_id.in_([user.user_id for user in Group.query.get(group_id).group])).all()
        return friends
    
    def get_friends_artists(self, group_id):
        friends = self.get_friends(group_id)
        return {friend.username: db.session.query(Artist).filter(Artist.artist_id.in_([art.artist_id for art in friend.artists])).all() for friend in friends}
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=3600 * 72):
        return jwt.encode({"reset_password": str(self.id), "exp": time() + expires_in}, config.SECRET_KEY, algorithm="HS256")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, config.SECRET_KEY, algorithms=["HS256"])["reset_password"]
        except:
            return
        return User.query.get(id)

    def __repr__(self):
        return "<User {}>".format(self.username)
    
    
    def add_user_to_group(self, group):
        if not isinstance(group, Group):
            raise ValueError("group must be an instance of the Group model")

        if group not in self.groups:
            self.groups.append(group)
            db.session.commit()
            
            
    def add_user_to_artist(self, artist):
        if not isinstance(artist, Artist):
            raise ValueError("artist must be an instance of the Artist model")

        if artist not in self.artists:
            self.artists.append(artist)
            db.session.commit()
            
    def remove_user_from_group(self, group):
        if not isinstance(group, Group):
            raise ValueError("group must be an instance of the Group model")

        if group in self.groups:
            self.groups.remove(group)
            db.session.commit()
            
    def remove_user_from_artist(self, artist):
        if not isinstance(artist, Artist):
            raise ValueError("artist must be an instance of the Artist model")

        if artist in self.artists:
            self.artists.remove(artist)
            db.session.commit()
            
    def get_id(self):
        return str(self.user_id)


@lm.user_loader
def load_user(id):
    return User.query.get(id)


class Artist(db.Model):
    
    __tablename__ = 'artist'
    
    artist_id = Column(Integer, primary_key=True)
    name = Column(String(280), nullable=False)
    stage = Column(String(280), nullable=False)
    startdate = Column(DateTime, nullable=False)
    enddate = Column(DateTime, nullable=False)
    starttime = Column(String, nullable=False)
    endtime = Column(String, nullable=False)
    festival = Column(String(280), nullable=False, default="Lowlands")
    day = Column(String(30), nullable=True)
    

class Group(db.Model):
    
    __tablename__ = 'group'
    
    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(String(280), nullable=False)
    owner_id = Column(Integer, nullable=False)