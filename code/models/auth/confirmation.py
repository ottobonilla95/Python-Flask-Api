from db import db
from time import time
from uuid import uuid4

CONFIRMATION_EXPIRATION_DELTA = 1800  # 30 minutes

class ConfirmationModel(db.Model):

    __tablename__ = 'confirmation'

    id = db.Column(db.String(50), primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user = db.relationship("UserModel")


    def __init__(self, user_id:int,**kwargs) :
        super().__init__(**kwargs)
        
        self.id = uuid4().hex
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_DELTA
        self.user_id = user_id


    @classmethod
    def find_by_id(cls, _id) -> "ConfirmationModel":
        return cls.query.filter_by(id =_id).first()

    @property
    def expired(self) -> bool:
        return time() > self.expire_at 

    def force_to_expire(self):
        if not self.expired:
            self.expire_at = int(time())
            self.save_to_db()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()


