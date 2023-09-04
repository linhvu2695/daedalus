from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from werkzeug.utils import secure_filename
from os import path
from . import AppConst

upload = Blueprint("upload", __name__)

@upload.route("/upload", methods=["POST"])
def upload_document():
    document = request.files[UploadConst.FIELD_CONTENT]

    if not document:
        flash(UploadConst.MESSAGE_MISSING_CONTENT, category="error")
        return redirect(url_for("views.home"))
    
    filename = secure_filename(document.filename)
    doctype, subtype = extract_types(document.mimetype)

    if doctype == DocumentConst.DOCTYPE_IMAGE:
        # update DB

        # save in storage
        document.save(path.join(current_app.config[AppConst.CONFIG_STORAGE_PATH], filename))

    flash(UploadConst.MESSAGE_UPLOAD_SUCCESS, category="success")
    return redirect(url_for("views.home"))
    
    
# Constants
class UploadConst:
    FIELD_CONTENT = "content"

    MESSAGE_UPLOAD_SUCCESS = "Upload success."
    MESSAGE_MISSING_CONTENT = "Missing upload content."

class DocumentConst:
    DOCTYPE_IMAGE = "image"

    EXTENSION_JPEG = "jpeg"

# Helpers
def extract_types(mimetype: str) -> (str, str):
    parts = mimetype.split("/")

    if len(parts) != 2:
        return None, None
    doctype = parts[0].strip()
    subtype = parts[1].strip()
    return doctype, subtype
