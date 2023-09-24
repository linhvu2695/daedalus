from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch
from os import path
from flask_login import LoginManager
import config

db = SQLAlchemy()
es = Elasticsearch()

def create_app():
    # Configuration management
    app = Flask(__name__)
    app.config[AppConst.CONFIG_SECRET_KEY] = config.CONFIG_SECRET_KEY
    app.config[AppConst.CONFIG_SQLALCHEMY_DATABASE_URI] = f"sqlite:///{config.DATABASE_NAME}"
    app.config[AppConst.CONFIG_STORAGE_PATH] = config.CONFIG_STORAGE_PATH
    app.config[AppConst.CONFIG_ELASTICSEARCH_HOST] = config.ELASTICSEARCH_HOST
    app.config[AppConst.CONFIG_ELASTICSEARCH_PORT] = config.ELASTICSEARCH_PORT
    app.config[AppConst.CONFIG_ELASTICSEARCH_INDEX_NAME] = config.ELASTICSEARCH_INDEX_NAME

    # Views management
    from .views import views
    from .auth import auth
    from .upload import upload
    from .files import files
    from .buffer import buffer
    from .elasticsearch.index import index

    for blueprint in [views, auth, upload, files, buffer, index]:
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

    # ElasticSearch management
    es.transport.hosts = [{"host": app.config[AppConst.CONFIG_ELASTICSEARCH_HOST], 
                           "port": app.config[AppConst.CONFIG_ELASTICSEARCH_PORT]}]
    create_index(app, es)

    return app


# Constants
class AppConst:
    CONFIG_SECRET_KEY = "SECRET_KEY"
    CONFIG_SQLALCHEMY_DATABASE_URI = "SQLALCHEMY_DATABASE_URI"
    CONFIG_STORAGE_PATH = "STORAGE_PATH"
    CONFIG_ELASTICSEARCH_HOST = "ELASTICSEARCH_HOST"
    CONFIG_ELASTICSEARCH_PORT = "ELASTICSEARCH_PORT"
    CONFIG_ELASTICSEARCH_INDEX_NAME = "ELASTICSEARCH_INDEX_NAME"

    DEFAULT_STORAGE_ID = 1
    DEFAULT_STORAGE_TITLE = "Storage"

    SEPARATOR_PATH = "/"

    SESSION_CURRENT_FOLDER_KEY = "current_folder"


# Helpers
def create_database(app: Flask):
    from .models import Document

    if not path.exists("website/" + config.DATABASE_NAME):
        db.create_all()
        print("Created Database.")

    default_storage = Document.query.filter_by(id=AppConst.DEFAULT_STORAGE_ID).first()
    if not default_storage:
        new_default_storage = Document(
            id=AppConst.DEFAULT_STORAGE_ID,
            title=AppConst.DEFAULT_STORAGE_TITLE,
            storage_path=app.config[AppConst.CONFIG_STORAGE_PATH],
            doctype=Document.Const.DOCTYPE_FOLDER,
            lineage_path=AppConst.DEFAULT_STORAGE_ID,
        )
        db.session.add(new_default_storage)
        db.session.commit()
        print("Default storage created.")


def create_index(app: Flask, es: Elasticsearch):
    if not es.indices.exists(index=app.config[AppConst.CONFIG_ELASTICSEARCH_INDEX_NAME]):
        es.indices.create(index=app.config[AppConst.CONFIG_ELASTICSEARCH_INDEX_NAME])
