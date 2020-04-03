from flask import Blueprint
from flask_restful import Api
from resources.store.store import Store, StoreList, StoreCreation, StoreByUser
from resources.store.item import Item, ItemList, ItemCreation

# Create bluepirnt
store_app = Blueprint('store', __name__)
api = Api(store_app)


# Add resources
# Stores
api.add_resource(Store, '/store/<int:id>')
api.add_resource(StoreList, '/stores')
api.add_resource(StoreByUser, '/ownstores')
api.add_resource(StoreCreation, '/store')

# Items
api.add_resource(Item, '/item/<int:id>')
api.add_resource(ItemList, '/items/<int:store_id>')
api.add_resource(ItemCreation, '/item')


