from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user

from .tools import request_tools
from . import db, es, AppConst
from .models import Keytype

keywords = Blueprint("keywords", __name__)
keytypes = Blueprint("keytypes", __name__)

# Keywords

@keywords.route("/keywords")
@login_required
def keywords_explore():
    return render_template("keywords.html", user=current_user)

@keywords.route("/keywords/search")
@login_required
def keywords_search():
    freetext_term = request.args.get("freetext-term")

    return render_template("keywords.html", user=current_user)

# Keytypes

@keytypes.route("/keytypes")
@login_required
def keytypes_explore():
    return render_template("keytypes.html", user=current_user, 
                           query=render_template("query/query.html", search_url="/keytypes/search"),
                           query_create=render_template("query/query_create.html", 
                                                        create_popup_id="create-keytype-popup",
                                                        popup=render_template("popup/keytypes_popup.html")))

@keytypes.route("/keytypes/search")
@login_required
def keytypes_search():
    freetext_term = request.args.get("freetext-term")

    keytypes = Keytype.query.filter(Keytype.name.like(f"%{freetext_term}%")).filter_by(binned=False).all()
    columns = [Keytype.Const.FIELD_ID,
               Keytype.Const.FIELD_NAME,
               Keytype.Const.FIELD_CREATE_DATE]
    results = []

    for keytype in keytypes:
        results.append(keytype.to_dict(columns))

    results.sort(key=lambda x: x[Keytype.Const.FIELD_CREATE_DATE], reverse=True)

    return render_template("query/search_results.html", user=current_user, 
                           results=results, columns=columns,
                           detail_popup_id="keytype-detail-popup")

@keytypes.route("/keytypes/create", methods=["POST"])
@login_required
def keytypes_create():
    keytype_name = request.form.get(Keytype.Const.FIELD_NAME)
    create_message = ""
    success = False

    if (len(keytype_name) == 0):
        return redirect(url_for("keytypes.keytypes_explore"))

    if (len(Keytype.query.filter_by(name=keytype_name).all()) == 0):
        new_keytype = Keytype(name=keytype_name)
        db.session.add(new_keytype)
        db.session.commit()
        create_message = f"New keytype created: {new_keytype.name}."
        success = True
    else:
        create_message = f"Keytype {keytype_name} already existed."
        success = False
    print(create_message)

    return jsonify(create_message=create_message, success=success)

@keytypes.route("/keytypes/detail/<int:id>")
@login_required
def keytypes_detail(id: int):
    if(request_tools.is_ajax_request(request)):
        keytype = Keytype.query.get(id)

        return jsonify(keytype.to_dict())
    
@keytypes.route("/keytypes/delete/<int:id>", methods=["POST"])
@login_required
def keytypes_delete(id: int):
    keytype = Keytype.query.get(id)
    success = False
    delete_message = ""

    if (keytype):
        keytype.binned = True
        db.session.commit()
        delete_message = f"Keytype {keytype.name} deleted successfully"
        success = True
    else:
        delete_message = f"Keytype id {id} not found"
        success = False

    return jsonify({"success": success,
                    "delete_message": delete_message})