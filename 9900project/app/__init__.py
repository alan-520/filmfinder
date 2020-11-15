from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_cors import CORS
from flask import Flask, render_template
import pymongo as pm
from app.config import Config

client = pm.MongoClient('mongodb+srv://alan:123456unsw@alandb.yzqdi.mongodb.net/test')
db = client.main

bootstrap = Bootstrap()
login_manager = LoginManager()
secure = Bcrypt()
mail = Mail()
cors = CORS()

def create_app():
    app = Flask(__name__, template_folder="templates", static_folder="static")
    app.config.from_object(Config)
    secure.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'guide.login'
    bootstrap.init_app(app)
    cors.init_app(app, supports_credentials=True)
    app.jinja_env.globals.update(__builtins__)

    from .guide import guide
    app.register_blueprint(guide, url_prefix='/guide')

    from .search import search
    app.register_blueprint(search, url_prefix='/search')

    from .details import details
    app.register_blueprint(details, url_prefix='/details')

    from .wishlist import wishlist
    app.register_blueprint(wishlist, url_prefix='/wishlist')

    @app.route('/')
    def welcome():
        return render_template('/welcome/welcome.html')
    '''@app.errorhandler(404)
    def miss(e):
        return render_template('/error/404.html'), 404

    @app.errorhandler(500)
    def error(e):
        return render_template('/error/500.html'), 500'''

    return app