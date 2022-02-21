from flask import jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin

db = SQLAlchemy()


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), unique=False, nullable=False)
    subscriptions = relationship("Subscription", back_populates="user")

class Manga(db.Model):
    __tablename__ = "manga"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=False, nullable=False)
    description = db.Column(db.Text, unique=False, nullable=False)
    thumbnail = db.Column(db.Text, unique=False, nullable=False)
    latest_chapter = db.Column(db.Float, unique=False, nullable=False)
    status = db.Column(db.String(100), unique=False, nullable=False)
    url = db.Column(db.String(250), unique=False, nullable=False)
    subscriptions = relationship("Subscription", back_populates="manga")

    def to_dict(self):
        row_as_dict = {column: str(getattr(self, column)) for column in self.__table__.c.keys()}
        return row_as_dict


class Subscription(db.Model):
    __tablename__ = "subscriptions"
    id = db.Column(db.Integer, primary_key=True)
    manga_id = db.Column(db.Integer, db.ForeignKey("manga.id"))
    manga = relationship("Manga", back_populates="subscriptions")
    endpoint = db.Column(db.JSON)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    user = relationship("User", back_populates="subscriptions")

