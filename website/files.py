from flask import Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from . import db, AppConst
from .models import Document
from .structure.document import *

files = Blueprint("files", __name__)

@files.route("/files")
@login_required
def files_explore():
    return render_template("files.html", user=current_user, 
                           browser_tree=get_rendered_document_tree(AppConst.DEFAULT_STORAGE_ID),
                           popup=render_template("popup.html"),
                           rightclick_menu=render_template("rightclick_menu.html"))

@files.route("/files/folder/<int:mother_id>", methods=["POST"])
def create_subfolder(mother_id):
    new_subfolder = Document(title=request.form.get(Document.Const.FIELD_TITLE), 
             doctype=Document.Const.DOCTYPE_FOLDER,
             mother=mother_id)
    db.session.add(new_subfolder)
    db.session.commit()
    print(f"New subfolder created: {new_subfolder.title}")

    return redirect(url_for("files.files_explore"))

@files.route("/files/folder/delete/<int:folder_id>", methods=["POST"])
def delete_folder(folder_id):
    children_query = Document.query.filter_by(mother=folder_id)

    # Delete all children documents
    sub_documents = children_query.filter(Document.doctype!=Document.Const.DOCTYPE_FOLDER).all()
    for doc in sub_documents:
        _delete_document(doc)

    # Delete all children folders recursively
    subfolders = children_query.filter_by(doctype=Document.Const.DOCTYPE_FOLDER).all()
    for subfolder in subfolders:
        delete_folder(subfolder.id)

    # Delete the folder itself
    folder = Document.query.get(folder_id)
    if (folder):
        if (folder.doctype != Document.Const.DOCTYPE_FOLDER):
            print(f"Document id {folder_id} is not a folder.")
        else:
            _delete_document(folder)
    else:
        print(f"Folder id {folder_id} not found")

    return redirect(url_for("files.files_explore"))

@files.route("files/doc/delete/<int:doc_id>", methods=["POST"])
def delete_document(doc_id):
    doc = Document.query.get(doc_id)
    if (doc):
        if (doc.doctype == Document.Const.DOCTYPE_FOLDER):
            print(f"Document {doc_id} is a folder.")
            print(f"To delete a folder via API, please use {url_for(delete_folder.__name__, folder_id=doc_id)}")
        else:
            _delete_document(doc)
    else:
        print(f"Document id {doc_id} not found")

    return redirect(url_for("files.files_explore"))

def _delete_document(document):
    """
    Function to actually delete the queried document in database.
    """
    db.session.delete(document)
    db.session.commit()
    print(f"Document {document.title} deleted successfully")

def get_rendered_document_tree(root_id: int) -> str:
    """
    Get the rendered HTML of the full document tree
    """
    return get_document_tree(root_id).render_tree()

def get_document_tree(root_id: int) -> DocumentTree:
    """
    Get a document tree 
    """
    # Get default storage
    root_document = Document.query.filter_by(
        id=root_id,
        ).first()
    if not root_document: return {}

    root_node = DocumentNode(root_document)

    children = Document.query.filter_by(mother=root_id).all()
    for child in children:
        child_node = get_document_tree(child.id).root
        root_node.add_child(child_node)

    # TODO: add chidren recursively

    doc_tree = DocumentTree()
    doc_tree.add_node(root_node)

    return doc_tree
