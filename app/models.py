from datetime import datetime, timezone

from flask.cli import prepare_import
from werkzeug.security import generate_password_hash, check_password_hash
from typing import Optional
from flask_login import UserMixin
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from hashlib import md5

# comes from the LoginManager object
# this function is called everytime a request is made that requires
# current_user. It then populates this information into current_user
@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))


followers = sa.Table(
    'followers',
    db.metadata,
    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True),
    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'), primary_key=True)
)

# These back_populates things basically make it so that if you define a post
# for this user, it will automatically add some "author" data in the Posts table for that user
# its a fancy way of updating both tables at the same time, if one, or the other is updated
# WriteOnlyMapped is basically the same as Mapped, but it wont load in queries unless specifically
# queried.
class User(UserMixin, db.Model):
    id:             so.Mapped[int] = so.mapped_column(primary_key=True)
    username:       so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email:          so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash:  so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts:          so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))
    # col name # expected data type         # how it relates to other columns
    following: so.WriteOnlyMapped['User'] = so.relationship(
        # says which table we are connecting
        secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers'
    )
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers,
        primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following'
    )


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<User {}'.format(self.username)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'

    def follow(self, user):
        if not self.is_following(user):
            self.following.add(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)

    def is_following(self, user):
        # User.id == user.id is kind of like saying where the "user" column = some specific ID
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None

    def followers_count(self):
        # this like SELECT COUNT(*) FROM (SUBQUERY)
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery()
        )
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery()
        )
        return db.session.scalar(query)

class Post(db.Model):
    id:         so.Mapped[int] = so.mapped_column(primary_key=True)
    body:       so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp:  so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id:    so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    author:     so.Mapped[User] = so.relationship(back_populates='posts')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(default=lambda: datetime.now(timezone.utc))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
