from datetime import datetime, timedelta
from time import time
import jwt

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Time, select, UniqueConstraint, func, text

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
    email = Column(String(80), nullable=True, unique=True)
    created = Column(DateTime, default=datetime.now())

    groups = db.relationship("Group", secondary=user_to_group, backref="group")
    artists = db.relationship("Artist", secondary=user_to_artist, backref="artist")

    def get_all_artists_ordered(self):
        stmt = select(Artist, (func.lead(Artist.startdate).over(order_by=Artist.startdate) - Artist.enddate).label('time_difference'))
        res = db.session.execute(stmt).all()
        print(res)
        return res

    def get_friends(self, group_id):
        friends = db.session.query(User).filter(User.user_id.in_([user.user_id for user in Group.query.get(group_id).group])).all()
        return friends

    def get_friends_artists(self, group_id):
        friends = self.get_friends(group_id)
        return {
            friend.username: db.session.query(Artist).filter(Artist.artist_id.in_([art.artist_id for art in friend.artists])).all()
            for friend in friends
        }

    def create_group(self, group_name):
        owner_of_group = Group.query().filter(Group.owner_id == self.user_id).all()
        if len(owner_of_group) > 3:
            return False, "You can't create more than 3 groups"
        else:
            group = Group(group_name=group_name, owner_id=self.user_id)
            db.session.add(group)
            db.session.commit()
            return True, "Group created"

    def invite_user_to_group(self, group_id: int, invited_user_id: int):
        check_user_groupmember = group_id in [group.group_id for group in self.groups]
        check_invited_user_groupmember = group_id in [group.group_id for group in User.query.get(invited_user_id).groups]
        invite_already_open = (
            len(GroupInvite.query.filter(GroupInvite.to_group_id == group_id, GroupInvite.to_user_id == invited_user_id).all()) > 0
        )
        if not check_user_groupmember:
            return False, "You are not a member of this group"
        if check_invited_user_groupmember:
            return False, "User is already a member of this group"
        if invite_already_open:
            return False, "User has already been invited"
        else:
            gadd = GroupInvite(to_group_id=group_id, from_user_id=self.user_id, to_user_id=invited_user_id)
            db.session.add(gadd)
            db.session.commit()
            return True, "User invited"

    def accept_group_invite(self, invite_id):
        group_invite = GroupInvite.query.get(invite_id)
        if group_invite.to_user_id != self.user_id:
            raise PermissionError("You are not the invited user")
        self.add_user_to_group(Group.query.get(group_invite.to_group_id))
        group_invite.accepted = True
        db.session.commit()

    def get_open_invites(self):
        open_invites = (
            GroupInvite.query.join(User, GroupInvite.from_user_id == User.user_id)
            .join(Group, GroupInvite.to_group_id == Group.group_id)
            .filter(GroupInvite.to_user_id == self.user_id, GroupInvite.accepted == False)
            .add_columns(GroupInvite.invite_id, User.username, Group.group_name)
            .all()
        )
        return open_invites

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

    def count_group_members(self, group_id):
        query = text("""SELECT COUNT(user_id) FROM user_to_group WHERE group_id = :group_id""")
        result = db.session.execute(query, {"group_id": group_id}).fetchone()[0]
        return result

    def get_group_details(self):
        groups = self.groups
        ## get the number of members in each group
        group_details = [
            {
                "group_name": group.group_name,
                "group_id": group.group_id,
                "members": self.count_group_members(group.group_id),
                "type": "Private" if group.private else "Public",
            }
            for group in groups
        ]
        return group_details

    def get_id(self):
        return str(self.user_id)


@lm.user_loader
def load_user(id):
    return User.query.get(id)


class Artist(db.Model):
    __tablename__ = "artist"

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
    __tablename__ = "group"

    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(String(280), nullable=False)
    owner_id = Column(Integer, nullable=False)
    private = Column(Boolean, nullable=True, default=True)


class GroupInvite(db.Model):
    __tablename__ = "group_invite"

    invite_id = Column(Integer, autoincrement=True, primary_key=True)
    to_group_id = Column(Integer, nullable=False)
    from_user_id = Column(Integer, nullable=False)
    to_user_id = Column(Integer, nullable=False)
    accepted = Column(Boolean, nullable=False, default=False)
    # token = Column(String(280), nullable=True)
    # created = Column(DateTime, nullable=False, default=datetime.utcnow)
    db.UniqueConstraint(to_group_id, to_user_id)
