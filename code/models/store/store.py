from db import db
from datetime import datetime

class StoreModel(db.Model):

    __tablename__ = 'store'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    description = db.Column(db.String(80))
    image = db.Column(db.String(255))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'),  nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def find_by_id(cls, _id) -> "StoreModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def get_all(cls) -> None:
        return cls.query.all()
    
    @classmethod
    def get_by_user(cls, _user_id) -> None:
        return cls.query.filter_by(user_id=_user_id)

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self) -> None:
        db.session.add(self)
        db.session.commit()
