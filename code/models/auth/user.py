from db import db
from datetime import datetime
from models.auth.confirmation import ConfirmationModel
from libs.mailgun import Mailgun
from flask import request, url_for
from requests import Response

class UserModel(db.Model):

    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64))
    email = db.Column(db.String(64))
    password = db.Column(db.String(100))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    admin = db.Column(db.Boolean, default=0)

    stores = db.relationship(
        "StoreModel", lazy="dynamic", cascade="all, delete-orphan")

    confirmation = db.relationship(
        "ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")

    @classmethod
    def find_by_username(cls, username) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_by_email(cls, _email) -> "UserModel":
        return cls.query.filter_by(email=_email).first()

    @classmethod
    def find_by_id(cls, id) -> "UserModel":
        return cls.query.filter_by(id=id).first()

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    def send_confirmation_email(self) -> Response:
        subject = "Registration Confirmation"

        link = request.host_url[:-1] + url_for(
            "auth.confirmation", confirmation_id=self.most_recent_confirmation.id
        )

        text = f"Please click the link to confirm your registration: {link}"
        html = f"<html>Please click the link to confirm your registration: <a href={link}>link</a></html>"

        return Mailgun.send_email([self.email], subject, text, html)

    def send_notification_email(self, message) -> Response:
        subject = "Store App"
        text = f"{message}"
        html = f"<html>{message}</html>"

        return Mailgun.send_email([self.email], subject, text, html)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
