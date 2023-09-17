from flask import Blueprint, send_file, abort
from flask_login import login_required
from . import AppConst

buffer = Blueprint("buffer", __name__)

@buffer.route("/buffer/<path:filepath>")
@login_required
def serve_file(filepath):
    try:
        # Send file directly from the original location
        return send_file("/" + filepath) 
    
        # TODO: implement buffering system

    except FileNotFoundError:
        print(f"FileNotFound error: {filepath}")
        abort(404)