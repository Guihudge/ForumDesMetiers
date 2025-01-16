from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db, login
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class User(UserMixin, db.Model):
    # TODO: add DisplayName and classe
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    rightLevel: so.Mapped[int] = so.mapped_column(sa.Integer(), default=0)

    def __repr__(self):
        return '<User {}, AccessLevel {}>'.format(self.username, self.rightLevel)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def set_access(self, level:int):
        self.rightLevel = level

class Jobs(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    Name: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True)

class TimeSlot(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    StartTime: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))
    EndTime: so.Mapped[datetime] = so.mapped_column(
        index=True, default=lambda: datetime.now(timezone.utc))

class WhishList(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), primary_key=True)
    first: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Jobs.id))
    second: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Jobs.id))
    third: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Jobs.id))
    fourth: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Jobs.id))
    fifth: so.Mapped[int] = so.mapped_column(sa.ForeignKey(Jobs.id))

class Student(db.Model):
    id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), primary_key=True)
    timeSlot: so.Mapped[int] = so.mapped_column(sa.ForeignKey(TimeSlot.id))
    whish: so.Mapped[int] = so.mapped_column(sa.ForeignKey(WhishList.id))


@login.user_loader
def load_user(id):
    return db.session.get(User, int(id))