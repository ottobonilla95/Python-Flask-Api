from flask_restful import Resource
from flask import request
from models.store.store import StoreModel
from models.store.item import ItemModel
from schemas.store.store import StoreSchema
from flask_jwt_extended import (
    jwt_required, get_jwt_identity, fresh_jwt_required)
from cdhandler import CloudinaryHandler
import json
from flask_babel import gettext

store_schema = StoreSchema()


class Store(Resource):

    @classmethod
    def get(cls, id):

        store = StoreModel.find_by_id(id)

        if store:
            return store_schema.dump(store)
        else:
            return {'Message': gettext('Store not found')}, 404

    @classmethod
    @fresh_jwt_required
    def delete(cls, id):

        store = StoreModel.find_by_id(id)

        if store:
            user = store.user
            store.delete_from_db()
            user.send_notification_email(
                f"You { store.name } store has been deleted !")

        return{'message': gettext('Store deleted')}, 200

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
    def get(cls):
        pagination = json.loads(request.args.get("pagination"))

        store_pagination = StoreModel.get_per_page(
            int(pagination["page"]))

        return {"stores": {"list": [store_schema.dump(store) for store in store_pagination.items], "pagination": {
            "page": store_pagination.page,
            "itemsPerPpage": store_pagination.per_page,
            "total": store_pagination.total,
            "pages": store_pagination.pages
        }}}


class StoreByUser(Resource):

    @fresh_jwt_required
    def get(cls):

        current_user = get_jwt_identity()

        pagination = json.loads(request.args.get("pagination"))

        store_pagination = StoreModel.get_by_user(current_user,
                                                  int(pagination["page"]))

        return {"stores": {"list": [store_schema.dump(store) for store in store_pagination.items], "pagination": {
            "page": store_pagination.page,
            "itemsPerPpage": store_pagination.per_page,
            "total": store_pagination.total,
            "pages": store_pagination.pages
        }}}

        return {'stores': [store_schema.dump(store) for store in StoreModel.get_by_user(current_user)]}


class StoreCreation(Resource):
    @classmethod
    @jwt_required
    def post(cls):

        store_json = request.get_json()["storeData"]
        user_id = get_jwt_identity()

        if "image" in store_json:
            image = CloudinaryHandler.LoadImage(store_json["image"])
            store_json["image"] = image

        store = store_schema.load(store_json)
        store.user_id = user_id
        store.save_to_db()

        user = store.user
        user.send_notification_email(
            f"You { store.name } store has been created !")

        return {'store': store_schema.dump(store)}, 200
