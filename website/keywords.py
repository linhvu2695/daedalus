from flask import Blueprint, render_template, request, jsonify, json
from flask_login import login_required, current_user

from .tools.request_tools import OptionList, is_ajax_request
from . import db, AppConst
from .query import query
from .models import Keytype, Keyword, Dockey

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

@keywords.route("keywords/all")
@login_required
def keywords_all():
    available_keywords = Keyword.query.filter_by(binned=False).all()

    option_list = OptionList()
    for keyword in available_keywords:
        option_list.add_option(keyword.id, keyword.name)

    return jsonify(option_list.to_list())

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

    return render_template("query/search_results.html", user=current_user, 
                           results=response, columns=columns,
                           detail_popup_id="keyword-detail-popup")

@keywords.route("/keywords/create", methods=["POST"])
@login_required
def keywords_create():
    keyword_name = request.form.get(Keyword.Const.FIELD_NAME)
    keytype_id = request.form.get(Keyword.Const.FIELD_KEYTPE)
    success = False
    message = ""

    if (len(keyword_name) == 0):
        return jsonify(message=message, success=success)
    
    exist_keytype = Keytype.query.get(keytype_id)
    if (exist_keytype == None):
        message = "Keytype not exist."
        return jsonify(message=message, success=success)

    if (len(Keyword.query.filter_by(name=keyword_name, keytype=keytype_id, binned=False).all()) == 0):
        new_keyword = Keyword(name=keyword_name, keytype=keytype_id)
        db.session.add(new_keyword)
        db.session.commit()
        message = f"New keyword created: {exist_keytype.name}.{new_keyword.name}."
        success = True
    else:
        message = f"Keyword {keyword_name} already existed."
        success = False
    print(message)

    return jsonify(message=message, success=success)

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

@keywords.route("/keywords/tag", methods=["POST"])
@login_required
def keywords_tag():
    doc_id = int(request.args.get("doc"))
    keywords = int(request.args.get("keywords"))
    success = False
    message = ""
    
    if (doc_id != None and doc_id > 0 and keywords != None and keywords > 0):
        # Check if the keyword is already tagged to the document
        existing_keywords = Dockey.query.filter_by(doc_id=doc_id, keyword_id=keywords, binned=0)
        if (existing_keywords.count() > 0):
            message = f"Keyword {keywords} is already tagged to document {doc_id}."
            return jsonify(message=message, success=success)
        
        new_dockey = Dockey(keyword_id=keywords, doc_id=doc_id)
        db.session.add(new_dockey)
        db.session.commit()
        message = f"Keyword {keywords} is tagged to document {doc_id}."
        success = True
    else:
        message = f"Invalid input: keyword {keywords} & document {doc_id}."
        success = False

    return jsonify(message=message, success=success)

@keywords.route("/keywords/doc/<int:doc_id>")
@login_required
def get_keywords_from_doc(doc_id: int):
    """
    Get all keywords tagged to a document.
    """
    columns = [Keyword.Const.FIELD_ID,
                Keyword.Const.FIELD_NAME]

    # Build query
    queryBuilder = query.QueryBuilder()
    queryBuilder.add_main_table("dockey DK")
    queryBuilder.add_join_table("JOIN keyword KW ON DK.keyword_id = KW.id")

    queryBuilder.add_field(f"KW.id AS {columns[0]}")
    queryBuilder.add_field(f"KW.name AS {columns[1]}")

    queryBuilder.add_where_condition(f"DK.doc_id = {doc_id}")
    queryBuilder.add_where_condition(f"KW.binned = 0")
    queryBuilder.add_where_condition(f"DK.binned = 0")
    queryBuilder.add_sort_field("KW.name")

    response = queryBuilder.get_query_result()
    return jsonify(response)

@keywords.route("/keywords/untag", methods=["POST"])
@login_required
def keyword_untag():
    doc_id = int(request.args.get("doc"))
    keywords = int(request.args.get("keywords"))
    success = False
    message = ""

    dockeys = Dockey.query.filter_by(doc_id=doc_id, keyword_id=keywords, binned=0)
    if (dockeys.count() == 0):
        message = f"Keyword {keywords} is not tagged to document {doc_id}."
        return jsonify(message=message, success=success)
    
    for dockey in dockeys:
        dockey.binned = True
        db.session.commit()
        print(f"Keyword {keywords} untag from document {doc_id} successfully")

    success = True
    return jsonify(success=success, message=message)

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
    message = ""
    success = False

    if (len(keytype_name) == 0):
        return jsonify(message=message, success=success)

    if (len(Keytype.query.filter_by(name=keytype_name, binned=False).all()) == 0):
        new_keytype = Keytype(name=keytype_name)
        db.session.add(new_keytype)
        db.session.commit()
        message = f"New keytype created: {new_keytype.name}."
        success = True
    else:
        message = f"Keytype {keytype_name} already existed."
        success = False
    print(message)

    return jsonify(message=message, success=success)

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