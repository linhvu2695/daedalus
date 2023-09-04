from . import create_app, db, AppConst
from .models import Document, DocumentConst

def init_db():
    app = create_app()
    with app.app_context():
        db.create_all()
        print("Database created.")

        _create_default_storage(app)

class InitDbConst:
    DEFAULT_STORAGE_ID = 1
    DEFAULT_STORAGE_TITLE = "storage"

# Helpers
def _create_default_storage(app):
    default_storage = Document.query.filter_by(id=InitDbConst.DEFAULT_STORAGE_ID).first()
    if not default_storage:
        new_default_storage = Document(
            id=InitDbConst.DEFAULT_STORAGE_ID, 
            title=InitDbConst.DEFAULT_STORAGE_TITLE,
            storage_path=app.config[AppConst.CONFIG_STORAGE_PATH],
            doctype=DocumentConst.DOCTYPE_FOLDER,
            )
        db.session.add(new_default_storage)
        db.session.commit()
        print("Default storage created.")

if __name__ == "__main__":
    init_db()