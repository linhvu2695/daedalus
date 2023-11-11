from flask import current_app
from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from io import BytesIO
from os import path
import uuid

from .. import db, AppConst
from ..models import Document
from ..elasticsearch import index
from ..exception.ingest_exception import *

# Constants

valid_filetypes = [Document.Const.DOCTYPE_IMAGE, Document.Const.DOCTYPE_AUDIO]

# Classes

class IngestResponse:
    """
    Response to ingest request.
    """
    def __init__(self, success: bool, mediatype: str, message: str) -> None:
        self.success = success
        self.mediatype = mediatype
        self.message = message

class IngestService:
    """
    Service to ingest documents
    """
    class Const:
        REPRESENTATIVE_IMAGES_PATH = "/representative_images"

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

class AudioIngestService(IngestService):
    """
    Service to ingest audios
    """
    def __init__(self):
        pass

    def ingest_document(self, mother_id: int, file: FileStorage):
        print(f"Processing {file.filename}...")

        original_filename = secure_filename(file.filename)
        filename = path.splitext(original_filename)[0]
        extension = original_filename.split('.')[-1]
        container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH]
        storage_path = container_path + AppConst.SEPARATOR_PATH + original_filename

        new_document = Document(title=filename,
                                doctype=Document.Const.DOCTYPE_AUDIO,
                                subtype=Document.Const.SUBTYPE_STANDARD_AUDIO,
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

        # Generate waveform image
        # waveform_image = AudioIngestService.generate_waveform(file)
        # container_path = current_app.config[AppConst.CONFIG_STORAGE_PATH] + IngestService.Const.REPRESENTATIVE_IMAGES_PATH
        # uid = str(uuid.uuid4())
        # with open(f"{original_filename}_{uid}.png", 'wb') as f:
        #     f.write(waveform_image.getvalue())

    @staticmethod
    def generate_waveform(file: FileStorage) -> BytesIO:
        """
        Generate a waveform image from an audio file.
        """
        original_filename = secure_filename(file.filename)
        filename = path.splitext(original_filename)[0]
        extension = original_filename.split('.')[-1]

        audio = AudioSegment.from_file(file, format=extension)
        
        # Create a figure and plot the waveform
        fig, ax = plt.subplots()
        ax.plot(audio.get_array_of_samples())

        # Save the figure to a BytesIO object
        output = BytesIO()
        FigureCanvas(fig).print_png(output)
        plt.close(fig)

        return output

# Public functions 

def ingest(mother_id: int, file: FileStorage) -> IngestResponse:
    mediatype, subtype = _extract_types(file.mimetype)

    success, message = False, ""
    try:
        if (mediatype not in valid_filetypes):
            raise IngestInvalidTypeException(f"Invalid filetype: {mediatype}")
        
        if mediatype == Document.Const.DOCTYPE_IMAGE:
            ingest_service = ImageIngestService()
        elif mediatype == Document.Const.DOCTYPE_AUDIO:
            ingest_service = AudioIngestService()

        ingest_service.ingest_document(mother_id, file)
        success = True

    except Exception as ex:
        message = str(ex)

    return IngestResponse(success, mediatype, message)

# Private functions

def _extract_types(mimetype: str) -> (str, str):
    parts = mimetype.split("/")

    if len(parts) != 2:
        return None, None
    doctype = parts[0].strip()
    subtype = parts[1].strip()
    return doctype, subtype