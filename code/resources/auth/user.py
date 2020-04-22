import datetime
from flask_restful import Resource
from flask import request
from models.auth.user import UserModel
from models.auth.confirmation import ConfirmationModel
from schemas.auth.user import UserSchema
from passlib.hash import pbkdf2_sha256
import traceback

from libs.mailgun import MailGunException
from flask_jwt_extended import (create_access_token,
                                get_jwt_identity,
                                create_refresh_token,
                                jwt_required,
                                jwt_refresh_token_required,
                                get_raw_jwt,
                                fresh_jwt_required)

from flask_babel import gettext
from uuid import uuid4

import os

user_schema = UserSchema()

timedelta = datetime.timedelta(minutes=int (os.environ.get('JWT_EXPIRATION_TIME', 5)))

custom_pbkdf2 = pbkdf2_sha256.using(rounds=296411)


class UserRegister(Resource):
    def post(self):

        user_json = request.get_json()["userData"]
        user = user_schema.load(user_json)

        try:

            if UserModel.find_by_username(user.username):
                return {"message": gettext('A user with that username already exists')}, 400

            if UserModel.find_by_email(user.email):
                return {"message":  gettext('A user with that email already exists')}, 400

            # Hash the password
            hashed_pass = custom_pbkdf2.hash(user.password)
            user.password = hashed_pass

            user.save_to_db()

            confirmation = ConfirmationModel(user.id)
            confirmation.save_to_db()
            user.send_confirmation_email()

            return {"message":  gettext('User successfully create, please confirm your email')}, 201

        except MailGunException as e:
            user.delete_from_db()
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            user.delete_from_db()  # rollback
            return {"message": gettext("Error when creating the user")}, 500


class User(Resource):

    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        if not user:
            return {'message':  gettext('User not found')}, 404

        return user_schema.dump(user), 200

    @classmethod
    @jwt_required
    def delete(cls):
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)

        if not user:
            return {'message': gettext('User not found')}, 404

        user.delete_from_db()

        return {'message':  gettext('User deleted')}, 200


class UserName(Resource):

    @classmethod
    @fresh_jwt_required
    def put(cls):

        user_id = get_jwt_identity()
        newusername = request.get_json()["userName"]

        if UserModel.find_by_username(newusername):
            return {"message": gettext('A user with that username already exists')}, 400
        else:
            user = UserModel.find_by_id(user_id)
            user.username = newusername
            user.save_to_db()

        return {"message":  gettext('Username updated')}, 200


class UserEmail(Resource):

    @classmethod
    @fresh_jwt_required
    def put(cls):

        user_id = get_jwt_identity()
        newemail = request.get_json()["userEmail"]

        if UserModel.find_by_email(newemail):
            return {"message": gettext('A user with that email already exists')}, 400
        else:

            try:
                user = UserModel.find_by_id(user_id)
                user.email = newemail
                user.save_to_db()

                confirmation = ConfirmationModel(user.id)
                confirmation.save_to_db()
                user.send_confirmation_email()

            except:
                return {"message":  gettext('Internal Error')}, 500

        return {"message":  gettext('Email updated')}, 200


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

            return {"message": gettext("Password updated")}, 200

        else:
            return {"message": gettext("Incorrect Password")}, 400


class UserResetPassword (Resource):

    @classmethod
    def post(cls):
        user_json = request.get_json()["userData"]
        userRecived = user_schema.load(user_json)

        userFound = UserModel.find_by_email(userRecived.email)

        if userFound:
            new_password = uuid4().hex
            hashed_pass = custom_pbkdf2.hash(new_password)
            userFound.password = hashed_pass
            userFound.save_to_db()

            userFound.send_notification_email(
                f"You new password is {new_password}")

            return {"message": gettext("We have sent you an email with your new password")}, 200
        else:
            return {'message': gettext('User not found')}, 404


class UserLogin(Resource):
    def post(self):

        try:
            user_json = request.get_json()["userData"]
            userRecived = user_schema.load(user_json)

            userFound = UserModel.find_by_username(userRecived.username)

            if userFound is None:
                userFound = UserModel.find_by_email(userRecived.username)

            # this is what the `authenticate()` function did in security.py
            if userFound and custom_pbkdf2.verify(userRecived.password, userFound.password):
                # identity= is what the identity() function did in security.py—now stored in the JWT

                confirmaion = userFound.most_recent_confirmation

                if confirmaion and confirmaion.confirmed:

                    expiration = datetime.datetime.now() + timedelta

                    access_token = create_access_token(
                        identity=userFound.id, fresh=True, expires_delta=timedelta)

                    refresh_token = create_refresh_token(userFound.id)

                    return {
                        "user_id": userFound.id,
                        "username": userFound.username,
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "expiration": expiration.isoformat()
                    }, 200

                return {"message":  gettext("Account not confirmed")}, 400

            return {"message":  gettext("Invalid Credentials")}, 404

        except Exception as e:
            return {"message": str(e)}, 500

class UserConfirmation(Resource):
    @classmethod
    def post (cls):
        user_json = request.get_json()["userData"]
        userRecived = user_schema.load(user_json)

        user = UserModel.find_by_email(userRecived.email)

        if not user:
            return {'message': gettext('User not found')}, 404

        try:
            confirmation = user.most_recent_confirmation

            if confirmation:
                if confirmation.confirmed:
                    return {"message":"Already confirmed"}, 400

                confirmation.force_to_expire()

            new_confirmation = ConfirmationModel(user.id)
            new_confirmation.save_to_db()

            user.send_confirmation_email()

            return {"message":  gettext('Confirmation email was sent')}, 200

        except MailGunException as e:
            return {"message": str(e)}, 500
        except:
            traceback.print_exc()
            return {"message":  gettext('Confirmation Resend Fail') }, 500

class UserLogout(Resource):
    @jwt_required
    def post(self):
        # jti = get_raw_jwt()['jti']  # jti is "JWT ID", a unique identifier for a JWT.
        # BLACKLIST.add(jti)
        return {"message": gettext("Logged out")}, 200


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):

        current_user = get_jwt_identity()
        new_token = create_access_token(
            identity=current_user, fresh=False, expires_delta=timedelta)
        expiration = datetime.datetime.now() + timedelta
        return {
            'access_token': new_token,
            "expiration": expiration.isoformat()
        }, 200
