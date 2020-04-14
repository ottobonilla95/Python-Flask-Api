import datetime
from flask_restful import Resource, reqparse
from flask import request
from models.user import UserModel
from models.store.store import StoreModel
from models.store.item import ItemModel
from schemas.user import UserSchema
from passlib.hash import pbkdf2_sha256

from flask_jwt_extended import (create_access_token,
                                get_jwt_identity,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_raw_jwt, 
                                fresh_jwt_required)

user_schema = UserSchema()
timedelta = datetime.timedelta(minutes=1)


custom_pbkdf2 = pbkdf2_sha256.using(rounds=296411)

class UserRegister(Resource):
    def post(self):
        
        user_json = request.get_json()["userData"]
        user = user_schema.load(user_json)
        
        original_pass = user.password
        hashed_pass = custom_pbkdf2.hash(user.password)
        user.password = hashed_pass
        
        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists"}, 400

        if UserModel.find_by_email(user.email):
            return {"message": "A user with that email already exists"}, 400

        user.save_to_db()

        return {"username": user.username, "password":original_pass}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404

        user.password = None
        return user_schema.dump(user), 200

    @classmethod
    @jwt_required
    def delete(cls):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User Not Found'}, 404

        # stores = StoreModel.
        # StoreModel.delete_by_user(user.id)


        user.delete_from_db()

        return {'message': 'User deleted.'}, 200


class UserName(Resource):
    
    @classmethod
    @fresh_jwt_required
    def put(cls):

        user_id = get_jwt_identity()
        newusername = request.get_json()["userName"]
       
        if UserModel.find_by_username(newusername):
            return {"Message": "Username already exists !"}, 400
        else:
            user = UserModel.find_by_id(user_id)
            user.username = newusername
            user.save_to_db()

        return {"Message":"Username updated !"}, 200


    
class UserEmail(Resource):

    @classmethod
    @fresh_jwt_required
    def put(cls):
        
        user_id = get_jwt_identity()
        newemail = request.get_json()["userEmail"]
       
        if UserModel.find_by_email(newemail):
            return {"Message": "Email already exists !"}, 400
        else:
            user = UserModel.find_by_id(user_id)
            user.email = newemail
            user.save_to_db()

        return {"Message":"Username updated !"}, 200
    
class UserPassword(Resource):

    @classmethod
    @fresh_jwt_required
    def put(cls):
        user_id = get_jwt_identity()
        currentPassword = request.get_json()["currentPassword"]
        newPassword = request.get_json()["newPassword"]

        user = UserModel.find_by_id(user_id)

        if custom_pbkdf2.verify(currentPassword, user.password):

            newHashedPassword = custom_pbkdf2.hash(newPassword)
            user.password = newHashedPassword
            user.save_to_db()

            return {"Message":"Password updated !"}, 200

        else:
            return {"Message":"Incorrect Password !"}, 400


class UserLogin(Resource):
    def post(self):

        try:
            user_json = request.get_json()["userData"]
            userRecived = user_schema.load(user_json)

            userFound = UserModel.find_by_username(userRecived.username)

            if userFound is None:
                userFound = UserModel.find_by_email(userRecived.email)

            # this is what the `authenticate()` function did in security.py
            if userFound and custom_pbkdf2.verify(userRecived.password, userFound.password):
                # identity= is what the identity() function did in security.py—now stored in the JWT
                
                expiration = datetime.datetime.now() + timedelta

                access_token = create_access_token(
                    identity=userFound.id, fresh=True, expires_delta= timedelta)

                refresh_token = create_refresh_token(userFound.id)

                return {
                    "user_id": userFound.id,
                    "username": userFound.username,
                    "access_token": access_token,
                    "refresh_token": refresh_token, 
                    "expiration" : expiration.isoformat()
                }, 200

            return {"message": "Invalid Credentials!"}, 401

        except:
            return {"message": "Internal Error!"}, 500

class UserLogout(Resource):
    @jwt_required
    def post(self):
        # jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a JWT.
        # BLACKLIST.add(jti)
        return {"message": "Successfully logged out"}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        """
        Get a new access token without requiring username and password—only the 'refresh token'
        provided in the /login endpoint.
        Note that refreshed access tokens have a `fresh=False`, which means that the user may have not
        given us their username and password for potentially a long time (if the token has been
        refreshed many times over).
        """
        current_user = get_jwt_identity()
        new_token = create_access_token(identity=current_user, fresh=False, expires_delta= timedelta)
        expiration = datetime.datetime.now() + timedelta
        return {
            'access_token': new_token,
            "expiration" : expiration.isoformat()
            }, 200
