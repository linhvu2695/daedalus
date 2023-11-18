from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from sqlalchemy import inspect

class BaseModel:
    def to_dict(self, filter=[]):
        if len(filter) > 0:
            columns = [column.name for column in self.__table__.columns if (column.name in filter)]
        else:
            columns = [column.name for column in self.__table__.columns]

        return {column: getattr(self, column) for column in columns}
    
class Contact(db.Model, BaseModel, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    first_name = db.Column(db.String(150))
    last_name = db.Column(db.String(150))
    login_id = db.Column(db.String(200))

    class Const:
        FIELD_ID = "id"
        FIELD_EMAIL = "email"
        FIELD_PASSWORD = "password"
        FIELD_FIRST_NAME = "first_name"
        FIELD_LAST_NAME = "last_name"
        FIELD_LOGIN_ID = "login_id"

    @staticmethod
    def columns() -> list[str]: 
        return [column.name for column in Contact.__table__.columns]

class Document(db.Model, BaseModel):
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
    description = db.Column(db.String(10000))

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
        FIELD_DESCRIPTION = "description"

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
        INDEXED_FIELD_LINEAGE_PATH = "LINEAGEPATH_STRING_INDEXED"
        INDEXED_FIELD_DESCRIPTION = "DESCRIPTION_TEXT_INDEXED"

        DOCTYPE_FOLDER = "folder"
        DOCTYPE_IMAGE = "image"
        DOCTYPE_AUDIO = "audio"

        SUBTYPE_STANDARD_IMAGE = "standard image"
        SUBTYPE_STANDARD_AUDIO = "standard audio"
    
    @staticmethod
    def columns() -> list[str]: 
        return [column.name for column in Document.__table__.columns]

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
            self.Const.INDEXED_FIELD_LINEAGE_PATH: self.lineage_path,
            self.Const.INDEXED_FIELD_DESCRIPTION: self.description,
        }
    
class Keytype(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(10000))
    binned = db.Column(db.Boolean, default=False)

    class Const:
        FIELD_ID = "id"
        FIELD_NAME = "name"
        FIELD_CREATE_DATE = "create_date"
        FIELD_DESCRIPTION = "description"
        FIELD_BINNED = "binned"
    
    @staticmethod
    def columns() -> list[str]: 
        return [column.name for column in Keytype.__table__.columns]

class Keyword(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    keytype = db.Column(db.Integer)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    description = db.Column(db.String(10000))
    binned = db.Column(db.Boolean, default=False)

    class Const:
        FIELD_ID = "id"
        FIELD_NAME = "name"
        FIELD_KEYTPE = "keytype"
        FIELD_CREATE_DATE = "create_date"
        FIELD_DESCRIPTION = "description"
        FIELD_BINNED = "binned"
    
    @staticmethod
    def columns() -> list[str]: 
        return [column.name for column in Keyword.__table__.columns]
    
class Dockey(db.Model, BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    doc_id = db.Column(db.Integer)
    keyword_id = db.Column(db.Integer)
    create_date = db.Column(db.DateTime(timezone=True), default=func.now())
    binned = db.Column(db.Boolean, default=False)

    class Const:
        FIELD_ID = "id"
        FIELD_DOC_ID = "doc_id"
        FIELD_KEYWORD_ID = "keyword_id"
        FIELD_CREATE_DATE = "create_date"
        FIELD_BINNED = "binned"

    @staticmethod
    def columns() -> list[str]: 
        return [column.name for column in Dockey.__table__.columns]

