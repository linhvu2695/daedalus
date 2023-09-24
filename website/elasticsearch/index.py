from flask import Blueprint
from flask_login import login_required
from .. import es, AppConst, files, jobs
from ..models import Document
import config

index = Blueprint("index", __name__)

@index.route("/index/doc/<int:doc_id>", methods=["POST"])
@login_required
def index_document_from_id(doc_id: int):
    """
    Index a document given its id
    """
    document = Document.query.get(doc_id)

    if (document):
        index_document(document)
    
    return files.open_current_folder_redirect()

@index.route("/index/doc/full", methods=["POST"])
@login_required
def index_document_full():
    """
    Reindex all documents.
    """
    all_documents = Document.query.all()

    if (all_documents):
        for doc in all_documents:
            index_document(doc)

    return jobs.jobs_explore()

def index_document(document: Document) -> bool:
    data = document.to_index_dict()
    index_name = config.ELASTICSEARCH_INDEX_NAME

    result = es.index(index=index_name,
                      document=data,
                      id=document.id)
    
    print(f"Indexing document {document.id} result: {result['result']}")