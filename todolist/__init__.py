from flask import Flask
import os
from dotenv import load_dotenv
from flask_login import LoginManager, login_manager
from flask_login.utils import logout_user
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from flask import Flask, session, redirect, url_for, flash
from datetime import datetime, timedelta
from flask_login import current_user
db = SQLAlchemy()

load_dotenv()
SECRET_KEY = os.environ.get("KEY")
DB_NAME = os.environ.get("DB_NAME")


def create_database(app):
    # if not os.path.exists("todolist/" + DB_NAME):
    with app.app_context():
        db.create_all()
        print("Created DB!")


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:Tranvantu%40294@localhost/pbl3"
    # app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)
    
    from .models import Note, User
    create_database(app)
    from .user import user
    from .views import views
    app.permanent_session_lifetime = timedelta(minutes=1)
    app.register_blueprint(user)
    app.register_blueprint(views)

    login_manager = LoginManager()
    login_manager.login_view = "user.login"
    login_manager.init_app(app)
    

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app
