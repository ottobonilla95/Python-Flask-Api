from ma import ma
from models.store.item import ItemModel

class ItemSchema(ma.ModelSchema):
    class Meta:
        include_fk = True
        model = ItemModel

