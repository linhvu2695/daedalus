from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from os import path
from .. import db, AppConst
from ..models import Document
from ..elasticsearch import index

class IngestService:
    """
    Service to ingest documents
    """
    def __init__(self):
        pass

    def ingest_document(self, mother_id: int, file: FileStorage):
        pass

class ImageIngestService(IngestService):
    """
    Service to ingest images
    """
    def __init__(self):
        pass

    def ingest_document(self, mother_id: int, file: FileStorage):
        print(f"Processing {file.filename}...")

        original_filename = secure_filename(file.filename)
        filename, extension = path.splitext(original_filename)
        container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH]
        storage_path = container_path + AppConst.SEPARATOR_PATH + original_filename

        new_document = Document(title=filename,
                                doctype=Document.Const.DOCTYPE_IMAGE,
                                subtype=Document.Const.SUBTYPE_STANDARD_IMAGE,
                                mother=mother_id,
                                storage_path=storage_path,
                                original_filename=original_filename,
                                extension=extension)
        db.session.add(new_document)
        db.session.commit()

        # Store the file in storage
        file.save(path.join(container_path, original_filename))

        # Update lineage_path
        mother_folder = Document.query.get(mother_id)
        new_document.lineage_path = mother_folder.lineage_path + AppConst.SEPARATOR_PATH + str(new_document.id)
        db.session.commit()

        # Index document
        index.index_document(new_document)
