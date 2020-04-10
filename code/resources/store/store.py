from flask_restful import Resource
from flask import request
from models.store.store import StoreModel
from models.store.item import ItemModel
from schemas.store.store import StoreSchema
from flask_jwt_extended import (jwt_required, get_jwt_identity, fresh_jwt_required)
from cdhandler import CloudinaryHandler;


store_schema = StoreSchema()

class Store(Resource):

    @classmethod
    def get(cls, id):

        store = StoreModel.find_by_id(id)

        if store:
            return store_schema.dump(store)
        else:
            return {'Message': 'No existe'}, 400

    @classmethod
    @fresh_jwt_required 
    def delete(cls, id):

        store = StoreModel.find_by_id(id)

        if store:
            ItemModel.delete_by_store(store.id)
            store.delete_from_db()

        return{'Message': 'Eliminado exitosamente'}, 200

    
    @classmethod
    @fresh_jwt_required 
    def put(cls, id):
        store_json = request.get_json()["storeData"]
        
        if "image" in store_json:
            if store_json["image"]:
                image = CloudinaryHandler.LoadImage(store_json["image"])
            else:
                image = None
            
            store_json["image"] = image
        
        store = StoreModel.find_by_id(id)

        if store:            
            store.name = store_json["name"]
            store.description = store_json["description"]
            
            if "image" in store_json:
                store.image = store_json["image"]
        else:
            store = store_schema.load(store_json)

        
        store.save_to_db()
        response = {'store': store_schema.dump(store)}, 200
        
        return response
    

class StoreList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        return {'stores': [store_schema.dump(store) for store in StoreModel.get_all()]}
    
class StoreByUser(Resource):
    
    @fresh_jwt_required    
    def get(cls):
        
        current_user = get_jwt_identity()
        return {'stores': [store_schema.dump(store) for store in StoreModel.get_by_user(current_user)]}


class StoreCreation(Resource):
    
    
    @classmethod
    @jwt_required 
    def post(cls):
        
        store_json = request.get_json()["storeData"]
   
        if  "image" in store_json:
            image = CloudinaryHandler.LoadImage(store_json["image"])
            store_json["image"] = image
        
        store = store_schema.load(store_json)
        store.save_to_db()
        return {'store': store_schema.dump(store)}, 200

        
        
