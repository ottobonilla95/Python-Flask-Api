from ma import ma
from models.store.store import StoreModel

class StoreSchema(ma.ModelSchema):
    class Meta:
        model = StoreModel
        include_fk = True

