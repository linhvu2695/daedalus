from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():

    # Configuration management
    app = Flask(__name__)
    app.config[AppConst.CONFIG_SECRET_KEY] = "mysecret"
    app.config[AppConst.CONFIG_SQLALCHEMY_DATABASE_URI] = f"sqlite:///{DB_NAME}"
    app.config[AppConst.CONFIG_STORAGE_PATH] = "storage" 

    # Views management
    from .views import views
    from .auth import auth
    from .upload import upload
    from .files import files

    for blueprint in [views, auth, upload, files]:
        app.register_blueprint(blueprint=blueprint, url_prefix="/")    

    # Database management
    with app.app_context():
        db.init_app(app)
        create_database(app)
        

    # Login management
    from .models import Contact
    
    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return Contact.query.get(int(id))

    return app

# Constants
class AppConst:
    CONFIG_SECRET_KEY  = "SECRET_KEY"
    CONFIG_SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    CONFIG_STORAGE_PATH = "STORAGE_PATH"

    DEFAULT_STORAGE_ID = 1
    DEFAULT_STORAGE_TITLE = "Storage"

# Helpers
def create_database(app):
    from .models import Document

    if not path.exists('website/' + DB_NAME):
        db.create_all()
        print('Created Database.')

    default_storage = Document.query.filter_by(id=AppConst.DEFAULT_STORAGE_ID).first()
    if not default_storage:
        new_default_storage = Document(
            id=AppConst.DEFAULT_STORAGE_ID, 
            title=AppConst.DEFAULT_STORAGE_TITLE,
            storage_path=app.config[AppConst.CONFIG_STORAGE_PATH],
            doctype=Document.Const.DOCTYPE_FOLDER,
            )
        db.session.add(new_default_storage)
        db.session.commit()
        print("Default storage created.")
    