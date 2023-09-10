from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db, AppConst
from .models import Document
from .structure.document import *

files = Blueprint("files", __name__)

@files.route("/files")
@login_required
def files_explore():
    return render_template("files.html", user=current_user, browser_tree=get_document_tree(AppConst.DEFAULT_STORAGE_ID))

@files.route("/files/<int:mother_id>", methods=["POST"])
def create_subfolder(mother_id):
    new_subfolder = Document(title=request.form.get(Document.Const.FIELD_TITLE), 
             doctype=Document.Const.DOCTYPE_FOLDER,
             mother=mother_id)
    db.session.add(new_subfolder)
    db.session.commit()
    print(f"New subfolder created: {new_subfolder.title}")

    return redirect(url_for("files.files_explore"))

def get_document_tree(root_id: int) -> str:
    """
    Get the rendered HTML of the full filesystem tree
    """
    # Get default storage
    root_document = Document.query.filter_by(
        id=root_id,
        ).first()
    if not root_document: return {}

    root_node = DocumentNode(root_document)

    children = Document.query.filter_by(mother=root_id).all()
    for child in children:
        root_node.add_child(DocumentNode(child))

    doc_tree = DocumentTree()
    doc_tree.add_node(root_node)

    return doc_tree.render_tree()