from flask import Blueprint
from flask_restful import Api
from resources.auth.user import (
    UserRegister,
    User,
    UserLogin,
    UserLogout,
    TokenRefresh,
    UserName,
    UserEmail,
    UserPassword, 
    UserResetPassword,
    UserConfirmation
    )

from resources.auth.confirmation import (
    ConfirmationByUser, Confirmation
)

# Create bluepirnt
auth_app = Blueprint('auth', __name__)
api = Api(auth_app)

# Add resources
# UserRegister
api.add_resource(UserRegister, '/usercreate')

# User
api.add_resource(User, '/user')
# User
api.add_resource(UserName, '/username')
# User
api.add_resource(UserEmail, '/useremail')
# User
api.add_resource(UserPassword, '/userpassword')
# UserLogin
api.add_resource(UserLogin, '/login')
# UserLogout
api.add_resource(UserLogout, '/logout')
# UserTokenRefresh
api.add_resource(TokenRefresh, '/tokenrefresh')

api.add_resource(Confirmation, '/user_confirm/<string:confirmation_id>')

api.add_resource(ConfirmationByUser, "/confirmation/user/<int:user_id>")

api.add_resource(UserResetPassword, "/userresetpassword")

api.add_resource(UserConfirmation, "/userconfirmationemail")



