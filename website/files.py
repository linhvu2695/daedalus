from flask import Blueprint, jsonify, session, render_template, request, redirect, url_for
from flask_login import login_required, current_user

from .services.ingest_service import *
from . import db, es, AppConst
from .models import Document
from .structure.document import *
from .elasticsearch import search, index

files = Blueprint("files", __name__)

@files.route("/files")
@login_required
def files_explore():
    return redirect(url_for("files.open_folder", folder_id=AppConst.DEFAULT_STORAGE_ID))

@files.route("/files/doc/detail/<int:doc_id>")
@login_required
def detail_document(doc_id: int):
    if(_is_ajax_request(request)):
        document = Document.query.get(doc_id)

        return jsonify(document.to_dict())

@files.route("/files/folder/<int:folder_id>")
@login_required
def open_folder(folder_id: int):
    # TODO: handle non-folder id

    session[AppConst.SESSION_CURRENT_FOLDER_KEY] = folder_id

    folder = Document.query.get(folder_id)
    documents = get_all_descendants_document(folder_id, session.get(AppConst.SESSION_CURRENT_SEETHRU_KEY, False))

    return get_rendered_files(documents, folder)

@files.route("/files/folder/create/<int:mother_id>", methods=["POST"])
@login_required
def create_subfolder(mother_id: int):
    new_subfolder = Document(title=request.form.get(Document.Const.FIELD_TITLE),
                             doctype=Document.Const.DOCTYPE_FOLDER,
                             mother=mother_id)
    db.session.add(new_subfolder)
    db.session.commit()
    print(f"New subfolder created: {new_subfolder.title}")

    # Update lineage_path
    mother_folder = Document.query.get(mother_id)
    new_subfolder.lineage_path = mother_folder.lineage_path + AppConst.SEPARATOR_PATH + str(new_subfolder.id)
    db.session.commit()

    # Index document
    index.index_document(new_subfolder)

    return open_current_folder_redirect()

@files.route("/files/doc/update/<int:doc_id>", methods=["POST"])
@login_required
def update_document(doc_id: int):
    document = Document.query.get(doc_id)

    print("Document metadata: " + str(request.form.to_dict()))

    if (document):
        for key, value in list(request.form.items()):
            if key == Document.Const.FIELD_TITLE:
                # rename
                document.title = value
                continue
            if key == Document.Const.FIELD_MOTHER:
                # move
                mother_id = int(value)
                mother_folder = Document.query.get(mother_id)
                if (mother_folder and mother_folder.doctype == Document.Const.DOCTYPE_FOLDER):
                    document.mother = mother_id
                    document.lineage_path = mother_folder.lineage_path + AppConst.SEPARATOR_PATH + str(document.id)
                    if _is_ajax_request(request):
                        db.session.commit()
                        index.index_document(document)
                        return jsonify(redirect=True, 
                                    redirect_url=url_for("files.open_folder", 
                                                            folder_id=session[AppConst.SESSION_CURRENT_FOLDER_KEY]))
                continue
            if key == Document.Const.FIELD_DESCRIPTION:
                # edit description
                document.description = value

        db.session.commit()
    print(f"Document {doc_id} updated.")

    # Reindex document
    index.index_document(document)

    return open_current_folder_redirect()

@files.route("/files/doc/upload/<int:mother_id>", methods=["POST"])
@login_required
def upload_document(mother_id: int):
    uploaded_files = request.files.getlist("content")

    for file in uploaded_files:
        mediatype, subtype = _extract_types(file.mimetype)

        if mediatype == Document.Const.DOCTYPE_IMAGE:
            ingest_service = ImageIngestService()
            ingest_service.ingest_document(mother_id, file)

    print(f"Upload to folder {mother_id}")

    return open_current_folder_redirect()

@files.route("/files/folder/delete/<int:folder_id>", methods=["POST"])
@login_required
def delete_folder(folder_id: int):
    children_query = Document.query.filter_by(mother=folder_id, binned=False)

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

    return open_current_folder_redirect()

@files.route("files/doc/delete/<int:doc_id>", methods=["POST"])
@login_required
def delete_document(doc_id: int):
    doc = Document.query.get(doc_id)
    if (doc):
        if (doc.doctype == Document.Const.DOCTYPE_FOLDER):
            print(f"Document {doc_id} is a folder.")
            print(f"To delete a folder via API, please use {url_for(delete_folder.__name__, folder_id=doc_id)}")
        elif (doc.binned == True):
            print(f"Document {doc_id} is already deleted.")
        else:
            _delete_document(doc)
    else:
        print(f"Document id {doc_id} not found")

    return open_current_folder_redirect()

@files.route("/seethru", methods=["POST"])
@login_required
def set_seethru():
    isActive = request.form.get("isActive") in ["true", "True"]
    session[AppConst.SESSION_CURRENT_SEETHRU_KEY] = isActive
    print(f"Seethru is set to: {isActive}")
    
    return jsonify(redirect=True, redirect_url=url_for("files.open_folder", folder_id=session[AppConst.SESSION_CURRENT_FOLDER_KEY]))

@files.route("/files/folder/<int:folder_id>/freetext")
@login_required
def freetext_search(folder_id: int):
    term = request.args.get("term")

    print (f"Search term: {term}")

    folder = Document.query.get(folder_id)

    builder = search.ESQueryBuilder()
    if (session.get(AppConst.SESSION_CURRENT_SEETHRU_KEY, False)):
        builder.add_term(Document.Const.INDEXED_LINEAGE_PATH, folder_id)
    else:
        builder.add_term(Document.Const.INDEXED_FIELD_MOTHER, folder_id)
    builder.add_wildcard(Document.Const.INDEXED_FIELD_TITLE, term)
    builder.set_retrieve_id_only()

    query = builder.build()
    print(f"Search query: {query}")

    response = search.ESQueryResponse(es.search(index=current_app.config[AppConst.CONFIG_ELASTICSEARCH_INDEX_NAME], body=query))
    print(f"Amount of matching results: {response.count}")
    print(f"Matching document ids: {response.get_ids()}")

    documents = []
    folder = Document.query.get(session[AppConst.SESSION_CURRENT_FOLDER_KEY])
    if (response.count > 0):
        documents = Document.query.filter(Document.id.in_(response.get_ids())).all()

    return get_rendered_files(documents, folder)

# Public functions

def open_current_folder_redirect():
    """
    Redirect to current folder view
    """
    return redirect(url_for("files.open_folder", folder_id=session[AppConst.SESSION_CURRENT_FOLDER_KEY]))

def get_rendered_browser_tree(root_id: int) -> str:
    """
    Get the rendered HTML of the full document tree
    """
    return get_document_tree(root_id, 
                             filtered_doctypes=[Document.Const.DOCTYPE_FOLDER], 
                             seethru=True,).render_tree()

def get_document_tree(root_id: int, filtered_doctypes=[], seethru=False) -> DocumentTree:
    """
    Get a document tree 

    Parameters:
        root_id (int): Root Folder ID 
        filtered_doctyes (list[str], optional): Doctypes to be included in the DocumentTree
        seethru (bool, optional): If the value is False, only retrieve direct children of the folder
    """
    # Get root document
    root_document = Document.query.filter_by(
        id=root_id,
        binned=False
        ).first()
    if not root_document: return {}

    root_node = DocumentNode(root_document)

    children_query = Document.query.filter_by(mother=root_id, binned=False)
    if len(filtered_doctypes) > 0:
        children_query = children_query.filter(Document.doctype.in_(filtered_doctypes))
    children = children_query.all()

    for child in children:
        if seethru:
            child_node = get_document_tree(child.id, filtered_doctypes, seethru).root
        else:
            child_node = DocumentNode(child)
        root_node.add_child(child_node)

    doc_tree = DocumentTree()
    doc_tree.add_node(root_node)

    return doc_tree

def get_rendered_asset_view(documents: list[Document], folder) -> str:
    """
    Get the rendered HTML of the asset view

    Parameters:
        documents: list of documents to be displayed
    """
    return render_template("asset_view.html", 
                           folder=folder,
                           documents=documents, 
                           breadcrumb=get_rendered_breadcrumb(folder.lineage_path))

def get_rendered_breadcrumb(lineage_path: str) -> str:
    lineage_ids = lineage_path.split(AppConst.SEPARATOR_PATH)
    if len(lineage_ids) == 0:
        print("Lineage path is missing")
        return ""

    try:
        lineage_records = Document.query.filter(Document.id.in_(lineage_ids)).all()
        records_id2title = {str(record.id): record.title for record in lineage_records}
    except Exception as e:
        print(f"Lineage path is corrupted. {e}")
        return ""

    return render_template("breadcrumb.html", 
                           id2title=records_id2title,
                           ancestor_ids=lineage_ids[:-1], 
                           current_id=lineage_ids[-1])

def get_all_descendants_document(folder_id: int, seethru=False) -> list[Document]:
    """
    Function to get all documents that are contained in a folder.

    Parameters:
        folder_id (int): Folder ID 
        seethru (bool, optional): If the value is False, only retrieve direct children of the folder
    """
    document_tree = get_document_tree(folder_id, seethru=seethru)
    return _get_all_descendants_document(document_tree.root)

def get_rendered_files(documents: list[Document], folder):
    """
    Get the rendered HTML of the files.

    Parameters:
        documents: list of documents to be displayed in asset view
        folder: should be the current folder
    """
    return render_template("files.html", user=current_user,
                           browser_tree=get_rendered_browser_tree(AppConst.DEFAULT_STORAGE_ID),
                           asset_view=get_rendered_asset_view(documents, folder),
                           popup=render_template("popup/popup.html"),
                           detail_popup=render_template("popup/detail_popup.html"),
                           rightclick_menu=render_template("rightclick_menu.html"),
                           seethru=render_template("seethru.html", current_seethru=session.get(AppConst.SESSION_CURRENT_SEETHRU_KEY, False)))

# Private functions

def _get_all_descendants_document(document_node: DocumentNode) -> list[Document]:
    """
    Helper function to get all documents that are contained in a folder in DFS manner.
    """
    documents = []

    for child in document_node.children:
        documents += [child.document]
        if (child.document.doctype == Document.Const.DOCTYPE_FOLDER):
            documents += _get_all_descendants_document(child)
    
    return documents

def _delete_document(document) -> None:
    """
    Function to actually delete the queried document in database.
    """
    document.binned = True
    db.session.commit()
    print(f"Document {document.title} deleted successfully")

    # Reindex document
    index.index_document(document)

def _extract_types(mimetype: str) -> (str, str):
    parts = mimetype.split("/")

    if len(parts) != 2:
        return None, None
    doctype = parts[0].strip()
    subtype = parts[1].strip()
    return doctype, subtype

def _is_ajax_request(request) -> bool:
    return request.headers.get("X-Requested-With") == "XMLHttpRequest"

def _extract_ancestor_ids(lineage_path: str) -> list[int]:
    if (len(lineage_path) == 0): return None
    return [int(num) for num in lineage_path.split('/')]