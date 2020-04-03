
from flask import Flask
from db import db
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager

#Modules
from modules.store import store_app
from modules.user import user_app

app = Flask(__name__)

#Add modules
app.register_blueprint(store_app)
app.register_blueprint(user_app)

CORS(app)
# cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

#Config
jwt = JWTManager(app)
app.config.from_object("config")



migrate = Migrate(app, db)

if __name__ == '__main__':
    db.init_app(app)
    app.run(debug=True)  # important to mention debug=True
