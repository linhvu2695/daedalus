from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func

class Contact(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))

    class Const:
        FIELD_ID = "id"
        FIELD_EMAIL = "email"
        FIELD_PASSWORD = "password"
        FIELD_FIRST_NAME = "first_name"
        FIELD_LAST_NAME = "last_name"

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(1000))
    storage_path = db.Column(db.String(10000))
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    doctype = db.Column(db.String(150))
    subtype = db.Column(db.String(150))
    mother = db.Column(db.Integer)
    binned = db.Column(db.Boolean, default=False)
    original_filename = db.Column(db.String(1000))
    extension = db.Column(db.String(20))

    class Const:
        FIELD_ID = "id"
        FIELD_TITLE = "title"
        FIELD_STORAGE_PATH = "storage_path"
        FIELD_CREATE_DATE = "create_date"
        FIELD_DOCTYPE = "doctype"
        FIELD_SUBTYPE = "subtype"
        FIELD_MOTHER = "mother"

        DOCTYPE_FOLDER = "folder"
        DOCTYPE_IMAGE = "image"

        SUBTYPE_STANDARD_IMAGE = "standard image"
