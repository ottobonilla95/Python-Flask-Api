from db import db
from datetime import datetime

class ItemModel(db.Model):

    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.Integer, db.ForeignKey('store.id'))
    name = db.Column(db.String(80))
    description = db.Column(db.String(80))
    price = db.Column(db.Float(precision=2))
    image = db.Column(db.String(255))
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    @classmethod
    def find_by_id(cls, _id) -> "ItemModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_store_id(cls, _id):
        return cls.query.filter_by(store_id=_id)
    
    @classmethod
    def get_all(cls):
        return cls.query.all()

    @classmethod
    def delete_by_store(cls, _store_id):
        cls.query.filter_by(store_id=_store_id).delete()


    def save_to_db(self)  -> None:
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self) -> None:
        db.session.delete(self)
        db.session.commit()
