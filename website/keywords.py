from flask import Blueprint, render_template, request, jsonify, json
from flask_login import login_required, current_user

from .tools.request_tools import OptionList, is_ajax_request
from . import db, AppConst
from .query import query
from .models import Keytype, Keyword

keywords = Blueprint("keywords", __name__)
keytypes = Blueprint("keytypes", __name__)

# Keywords

@keywords.route("/keywords")
@login_required
def keywords_explore():
    return render_template("keywords.html", user=current_user, 
                           query=render_template("query/query.html", search_url="/keywords/search"),
                           query_create=render_template("query/query_create.html", 
                                                        create_popup_id="create-keyword-popup",
                                                        popup=render_template("popup/keywords_popup.html")))

@keywords.route("/keywords/search")
@login_required
def keywords_search():
    freetext_term = request.args.get("freetext-term")
    columns = [Keyword.Const.FIELD_ID,
               Keyword.Const.FIELD_NAME,
               Keyword.Const.FIELD_KEYTPE,
               Keyword.Const.FIELD_CREATE_DATE]

    # Build query
    queryBuilder = query.QueryBuilder()
    queryBuilder.add_main_table("keyword KW")
    queryBuilder.add_join_table("JOIN keytype KT ON KW.keytype = KT.id")

    queryBuilder.add_field(f"KW.id AS {columns[0]}")
    queryBuilder.add_field(f"KW.name AS {columns[1]}")
    queryBuilder.add_field(f"KT.name AS {columns[2]}")
    queryBuilder.add_field(f"KW.create_date AS {columns[3]}")

    queryBuilder.add_where_condition(f"KW.name LIKE '%{freetext_term}%'")
    queryBuilder.add_where_condition(f"KW.binned = 0")
    queryBuilder.add_sort_field("KW.create_date DESC")

    response = queryBuilder.get_query_result()
    results = json.loads(response.get_data(as_text=True))
    

    return render_template("query/search_results.html", user=current_user, 
                           results=results, columns=columns,
                           detail_popup_id="keyword-detail-popup")

@keywords.route("/keywords/create", methods=["POST"])
@login_required
def keywords_create():
    keyword_name = request.form.get(Keyword.Const.FIELD_NAME)
    keytype_id = request.form.get(Keyword.Const.FIELD_KEYTPE)
    create_message = ""
    success = False

    if (len(keyword_name) == 0):
        return jsonify(create_message=create_message, success=success)
    
    exist_keytype = Keytype.query.get(keytype_id)
    if (exist_keytype == None):
        create_message = "Keytype not exist."
        return jsonify(create_message=create_message, success=success)

    if (len(Keyword.query.filter_by(name=keyword_name, keytype=keytype_id, binned=False).all()) == 0):
        new_keyword = Keyword(name=keyword_name, keytype=keytype_id)
        db.session.add(new_keyword)
        db.session.commit()
        create_message = f"New keyword created: {exist_keytype.name}.{new_keyword.name}."
        success = True
    else:
        create_message = f"Keyword {keyword_name} already existed."
        success = False
    print(create_message)

    return jsonify(create_message=create_message, success=success)

@keywords.route("/keywords/detail/<int:id>")
@login_required
def keywords_detail(id: int):
    if(is_ajax_request(request)):
        keyword = Keyword.query.get(id)

        return jsonify(keyword.to_dict())

@keywords.route("/keywords/delete/<int:id>", methods=["POST"])
@login_required
def keywords_delete(id: int):
    keyword = Keyword.query.get(id)
    success = False
    delete_message = ""

    if (keyword):
        keyword.binned = True
        db.session.commit()
        delete_message = f"Keyword {keyword.name} deleted successfully"
        success = True
    else:
        delete_message = f"Keyword id {id} not found"
        success = False

    return jsonify({"success": success,
                    "delete_message": delete_message})

# Keytypes

@keytypes.route("/keytypes")
@login_required
def keytypes_explore():
    return render_template("keytypes.html", user=current_user, 
                           query=render_template("query/query.html", search_url="/keytypes/search"),
                           query_create=render_template("query/query_create.html", 
                                                        create_popup_id="create-keytype-popup",
                                                        popup=render_template("popup/keytypes_popup.html")))

@keytypes.route("keytypes/all")
@login_required
def keytypes_all():
    available_keytypes = Keytype.query.filter_by(binned=False).all()

    option_list = OptionList()
    for keytype in available_keytypes:
        option_list.add_option(keytype.id, keytype.name)

    return jsonify(option_list.to_list())

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
        return jsonify(create_message=create_message, success=success)

    if (len(Keytype.query.filter_by(name=keytype_name, binned=False).all()) == 0):
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
    if(is_ajax_request(request)):
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