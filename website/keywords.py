from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
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

    keytypes = Keytype.query.filter(Keytype.name.like(f"%{freetext_term}%")).all()
    columns = [Keytype.Const.FIELD_ID, 
               Keytype.Const.FIELD_NAME, 
               Keytype.Const.FIELD_CREATE_DATE]
    results = []

    for keytype in keytypes:
        results.append({Keytype.Const.FIELD_ID: keytype.id,
                        Keytype.Const.FIELD_NAME: keytype.name,
                        Keytype.Const.FIELD_CREATE_DATE: keytype.create_date})

    results.sort(key=lambda x: x[Keytype.Const.FIELD_CREATE_DATE], reverse=True)

    return render_template("query/search_results.html", user=current_user, 
                           results=results, columns=columns)

@keytypes.route("/keytypes/create", methods=["POST"])
@login_required
def keytypes_create():
    keytype_name = request.form.get(Keytype.Const.FIELD_NAME)
    create_new_message = ""
    success = False

    if (len(keytype_name) == 0):
        return redirect(url_for("keytypes.keytypes_explore"))

    if (len(Keytype.query.filter_by(name=keytype_name).all()) == 0):
        new_keytype = Keytype(name=keytype_name)
        db.session.add(new_keytype)
        db.session.commit()
        create_new_message = f"New keytype created: {new_keytype.name}."
        success = True
    else:
        create_new_message = f"Keytype {keytype_name} already existed."
        success = False
    print(create_new_message)

    return jsonify(create_new_message=create_new_message, success=success)

