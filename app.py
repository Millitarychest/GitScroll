
from flask import Flask, redirect, render_template, request


from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_login import (
    UserMixin,
    login_user,
    LoginManager,
    current_user,
    logout_user,
    login_required,
)



#setups
login_manager = LoginManager()
login_manager.session_protection = "strong"
login_manager.login_view = "login"

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()


#web app
def create_app():
    app = Flask(__name__, static_url_path='', static_folder='templates/blog')
    
    app.secret_key = 'secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True

    login_manager.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)

    return app


