from flask_restful import Resource, reqparse
from flask import request
from models.user import UserModel
from schemas.user import UserSchema
from werkzeug.security import safe_str_cmp

from flask_jwt_extended import (create_access_token,
                                get_jwt_identity,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_raw_jwt)

user_schema = UserSchema()


class UserRegister(Resource):
    def post(self):
        user = user_schema.load(request.get_json())

        if UserModel.find_by_username(user.username):
            return {"message": "A user with that username already exists"}, 400

        user.save_to_db()

        return {"username": user.username, "password":user.password}, 201


class User(Resource):
    """
    This resource can be useful when testing our Flask app. We may not want to expose it to public users, but for the
    sake of demonstration in this course, it can be useful when we are manipulating data regarding the users.
    """
    @classmethod
    def get(cls, user_id: int):
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message': 'User Not Found'}, 404

        return user_schema.dump(user), 200

    @classmethod
    def delete(cls, user_id: int):
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': 'User Not Found'}, 404

        user.delete_from_db()

        return {'message': 'User deleted.'}, 200


class UserLogin(Resource):
    def post(self):

        userRecived = user_schema.load(request.get_json())

        userFound = UserModel.find_by_username(userRecived.username)

        # this is what the `authenticate()` function did in security.py
        if userFound and safe_str_cmp(userFound.password, userRecived.password):
            # identity= is what the identity() function did in security.py—now stored in the JWT
            access_token = create_access_token(
                identity=userFound.id, fresh=True)
            refresh_token = create_refresh_token(userFound.id)
            return {
                "user_id": userFound.id,
                "username": userFound.username,
                "access_token": access_token,
                "refresh_token": refresh_token 
            }, 200

        return {"message": "Invalid Credentials!"}, 401


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
        new_token = create_access_token(identity=current_user, fresh=False)
        return {'access_token': new_token}, 200
