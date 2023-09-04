from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import AppConst
from .models import Document
from .structure.document import *

files = Blueprint("files", __name__)

@files.route("/files")
@login_required
def files_explore():
    filesystem_html = get_filesystem_html()
    return render_template("files.html", user=current_user, filesystem_html=filesystem_html)

def get_filesystem_html() -> str:
    # Get default storage
    default_storage = Document.query.filter_by(
        id=AppConst.DEFAULT_STORAGE_ID, 
        title=AppConst.DEFAULT_STORAGE_TITLE
        ).first()
    if not default_storage: return {}

    doc_tree = DocumentTree(default_storage)

    return doc_tree.render_tree()