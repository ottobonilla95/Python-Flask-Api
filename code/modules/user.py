from flask import Blueprint
from flask_restful import Api
from resources.user import UserRegister, User, UserLogin, UserLogout, TokenRefresh

# Create bluepirnt
user_app= Blueprint('user', __name__)
api = Api(user_app)


# Add resources
# UserRegister
api.add_resource(UserRegister, '/usercreate')

#User
api.add_resource(User, '/user/<int:user_id>')

#UserLogin
api.add_resource(UserLogin, '/login')

#UserLogout
api.add_resource(UserLogout, '/logout')

#UserTokenRefresh
api.add_resource(TokenRefresh, '/tokenrefresh')

