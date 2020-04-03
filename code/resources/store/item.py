from flask import request
from flask_restful import Resource
from models.store.item import ItemModel
from schemas.store.item import ItemSchema

item_schema = ItemSchema()

class Item(Resource):

    def get(self, id):

        item = ItemModel.find_by_id(id)

        if item:
            return item_schema.dump(item)

        return {'message': 'Item not found'}, 404
    
    def delete(self, id):
        item = ItemModel.find_by_id(id)

        if item:
            item.delete_from_db()
            return {'message': 'Item deleted'}

        return {'message': 'Not found'}

    def put(self, id):
        
        item_json = request.get_json()["itemData"]
        item = ItemModel.find_by_id(id)

        if item:
            item.name = item_json["name"]
            item.description = item_json["description"]
            item.price = item_json["price"]
        else:
            item = item_schema.load(item_json)

        item.save_to_db()
        
        return {'item': item_schema.dump(item)}, 200



class ItemList(Resource):
    
    @classmethod
    def get(self, store_id):
        return {'items': [item_schema.dump(item) for item in ItemModel.find_by_store_id(store_id)]}


class ItemCreation(Resource):
    def post(self):
        
        item = item_schema.load(request.get_json()["itemData"])        
        
        item.save_to_db()
        return {'item':item_schema.dump(item)},200


