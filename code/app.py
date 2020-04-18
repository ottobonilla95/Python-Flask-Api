from flask import Flask, g, request
from flask_babel import Babel
from flask_cors import CORS
from flask_jwt_extended import JWTManager


# Modules
from modules.store import store_app
from modules.auth import auth_app

app = Flask(__name__)

# Add modules
app.register_blueprint(store_app)
app.register_blueprint(auth_app)

CORS(app)
babel = Babel(app)

@app.route("/ping")
def test():
    return {"message":"response"}, 200

@babel.localeselector
def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = getattr(g, 'user', None)
    if user is not None:
        return user.locale
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    # print("aja", request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'].keys()))
    return request.accept_languages.best_match(app.config['SUPPORTED_LANGUAGES'].keys())


@babel.timezoneselector
def get_timezone():
    user = getattr(g, 'user', None)
    if user is not None:
        return user.timezone


# Config
jwt = JWTManager(app)
app.config.from_object("config")

if __name__ == '__main__':
    from db import db
    db.init_app(app)

    app.run(debug=True)  # important to mention debug=True
