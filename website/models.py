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
    lineage_path = db.Column(db.String(10000))

    class Const:
        FIELD_ID = "id"
        FIELD_TITLE = "title"
        FIELD_STORAGE_PATH = "storage_path"
        FIELD_CREATE_DATE = "create_date"
        FIELD_DOCTYPE = "doctype"
        FIELD_SUBTYPE = "subtype"
        FIELD_MOTHER = "mother"
        FIELD_BINNED = "binned"
        FIELD_ORIGINAL_FILENAME = "original_filename"
        FIELD_EXTENSION = "extension"
        FIELD_LINEAGE_PATH = "lineage_path"

        INDEXED_FIELD_ID = "ID_STRING_INDEXED"
        INDEXED_FIELD_TITLE = "TITLE_TEXT_INDEXED"
        INDEXED_FIELD_STORAGE_PATH = "STORAGEPATH_TEXT_INDEXED"
        INDEXED_FIELD_CREATE_DATE = "CREATEDATE_DATE_INDEXED"
        INDEXED_FIELD_DOCTYPE = "DOCTYPE_STRING_INDEXED"
        INDEXED_FIELD_SUBTYPE = "SUBTYPE_STRING_INDEXED"
        INDEXED_FIELD_ORIGINAL_FILENAME = "ORIGINALFILENAME_STRING_INDEXED"
        INDEXED_FIELD_EXTENSION = "EXTENSION_STRING_INDEXED"
        INDEXED_FIELD_MOTHER = "MOTHER_STRING_INDEXED"
        INDEXED_FIELD_BINNED = "BINNED_BOOLEAN_INDEXED"

        DOCTYPE_FOLDER = "folder"
        DOCTYPE_IMAGE = "image"

        SUBTYPE_STANDARD_IMAGE = "standard image"

    def to_index_dict(self):
        """
        Convert the Document object to a dictionary.
        """
        return {
            self.Const.INDEXED_FIELD_ID: str(self.id),
            self.Const.INDEXED_FIELD_TITLE: self.title,
            self.Const.INDEXED_FIELD_STORAGE_PATH: self.storage_path,
            self.Const.INDEXED_FIELD_CREATE_DATE: self.create_date,
            self.Const.INDEXED_FIELD_DOCTYPE: self.doctype,
            self.Const.INDEXED_FIELD_SUBTYPE: self.subtype,
            self.Const.INDEXED_FIELD_ORIGINAL_FILENAME: self.original_filename,
            self.Const.INDEXED_FIELD_EXTENSION: self.extension,
            self.Const.INDEXED_FIELD_MOTHER: self.mother,
            self.Const.INDEXED_FIELD_BINNED: self.binned,
        }
