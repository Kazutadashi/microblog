from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

# These back_populates things basically make it so that if you define a post
# for this user, it will automatically add some "author" data in the Posts table for that user
# its a fancy way of updating both tables at the same time, if one, or the other is updated
# WriteOnlyMapped is basically the same as Mapped, but it wont load in queries unless specifically
# queried.
class User(db.Model):
    id:             so.Mapped[int] = so.mapped_column(primary_key=True)
    username:       so.Mapped[str] = so.mapped_column(sa.String(64), index=True, unique=True)
    email:          so.Mapped[str] = so.mapped_column(sa.String(120), index=True, unique=True)
    password_hash:  so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    posts:          so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')

    def __repr__(self):
        return '<User {}'.format(self.username)

class Post(db.Model):
    id:         so.Mapped[int] = so.mapped_column(primary_key=True)
    body:       so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp:  so.Mapped[datetime] = so.mapped_column(index=True, default=lambda: datetime.now(timezone.utc))
    user_id:    so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)
    author:     so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)