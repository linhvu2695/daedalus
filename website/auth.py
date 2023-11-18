from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app, session
from flask_login import login_user, login_required, logout_user, current_user
from authlib.integrations.flask_client import OAuth
from werkzeug.security import generate_password_hash, check_password_hash
import secrets
import json, re

from .models import Contact
from . import db, AppConst


auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if AppConst.SESSION_USER_INFO_KEY in session:
        user_info_dict = json.loads(session[AppConst.SESSION_USER_INFO_KEY])
        user_info = UserInfo(login_id=user_info_dict["login_id"], 
                             email=user_info_dict["email"], 
                             is_sso=user_info_dict["is_sso"])
        if user_info.is_sso:
            # Login via SSO
            email, login_id = user_info.email, user_info.login_id
            print(f"User logged in via SSO: {login_id}")
            contact = Contact.query.filter_by(email=email).first()

            if contact:
                # Contact already exist. Login using that contact
                flash(LoginConst.MESSAGE_LOGIN_SUCCESS, category="success")
                login_user(contact, remember=True)
                return(redirect(url_for("views.home")))
            else:
                # Contact not exist. Create new contact
                new_contact = Contact(email=email, login_id=login_id)
                db.session.add(new_contact)
                db.session.commit()
                
                login_user(new_contact, remember=True)
                flash(RegisterConst.MESSAGE_ACCOUNT_CREATED, category="success")
                return redirect(url_for("views.home"))
                
    else:
        if request.method == "POST":
            # Login via username & password
            email = request.form.get(LoginConst.FIELD_EMAIL)
            password = request.form.get(LoginConst.FIELD_PASSWORD)

            contact = Contact.query.filter_by(email=email).first()
            if contact:
                if check_password_hash(contact.password, password):
                    flash(LoginConst.MESSAGE_LOGIN_SUCCESS, category="success")
                    login_user(contact, remember=True)
                    return(redirect(url_for("views.home")))
                else:
                    flash(LoginConst.MESSAGE_INCORRECT_PASSWORD, category="error")
            else:
                flash(LoginConst.MESSAGE_NONEXIST_EMAIL, category="error")


    return render_template("login.html", user=current_user)

@auth.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop(AppConst.SESSION_USER_INFO_KEY, None)
    return redirect(url_for("auth.login"))

@auth.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get(RegisterConst.FIELD_EMAIL)
        firstname = request.form.get(RegisterConst.FIELD_FIRSTNAME)
        lastname = request.form.get(RegisterConst.FIELD_LASTNAME)
        password = request.form.get(RegisterConst.FIELD_PASSWORD)
        password_confirm = request.form.get(RegisterConst.FIELD_PASSWORD_CONFIRM)

        contact = Contact.query.filter_by(email=email).first()
        login_id = _get_username_from_email(email)
        
        if contact:
            flash(RegisterConst.MESSAGE_EMAIL_ALREADY_EXIST, category="error")
        elif len(email) < 4:
            flash(RegisterConst.MESSAGE_SHORT_EMAIL, category="error")
        elif len(firstname) < 2:
            flash(RegisterConst.MESSAGE_SHORT_FIRSTNAME, category="error")
        elif len(lastname) < 2:
            flash(RegisterConst.MESSAGE_SHORT_LASTNAME, category="error")
        elif password != password_confirm:
            flash(RegisterConst.MESSAGE_PASSWORD_MISMATCH, category="error")
        elif len(password) < 7:
            flash(RegisterConst.MESSAGE_SHORT_PASSWORD, category="error")
        elif login_id == None:
            flash(RegisterConst.MESSAGE_INVALID_EMAIL, category="error")
        else:
            # add to db
            new_contact = Contact(
                email=email, first_name=firstname, last_name=lastname, 
                password=generate_password_hash(password, method="sha256"),
                login_id=login_id)
            db.session.add(new_contact)
            db.session.commit()
            
            login_user(new_contact, remember=True)
            flash(RegisterConst.MESSAGE_ACCOUNT_CREATED, category="success")
            return redirect(url_for("views.home"))

    return render_template("register.html", user=current_user)

@auth.route("/sso", methods=["POST"])
def sso_handle():
    github = _get_github_oauth()
    random_nonce = secrets.token_urlsafe(16)
    return github.authorize_redirect(redirect_uri=url_for("auth.sso_callback", _external=True), nonce=random_nonce)

@auth.route("/callback")
def sso_callback():
    github = _get_github_oauth()
    token = github.authorize_access_token()
    print(f"Token: {token}")
    random_nonce = request.args.get("nonce")

    #Call github API for user info
    response = github.get(f"https://api.github.com/user?acces_token={token['access_token']}")
    response_json = json.loads(response.text)
    print(f"Response: {response_json}")
    login_id = response_json["login"]
    email = login_id + RegisterConst.GITHUB_EMAIL_DOMAIN
    session[AppConst.SESSION_USER_INFO_KEY] = json.dumps(UserInfo(login_id, email, is_sso=True).to_dict())
    return redirect(url_for('auth.login'))


# Constants
class RegisterConst:
    FIELD_FIRSTNAME = "firstName"
    FIELD_LASTNAME = "lastName"
    FIELD_EMAIL = "email"
    FIELD_PASSWORD = "password"
    FIELD_PASSWORD_CONFIRM = "passwordConfirm"

    MESSAGE_ACCOUNT_CREATED = "Account created!"
    MESSAGE_EMAIL_ALREADY_EXIST = "Email already exists. Please use another email."
    MESSAGE_SHORT_EMAIL = "Email must be greater than 3 characters."
    MESSAGE_SHORT_FIRSTNAME = "First name must be greater than 1 character."
    MESSAGE_SHORT_LASTNAME = "Last name must be greater than 1 character."
    MESSAGE_PASSWORD_MISMATCH = "Passwords don't match."
    MESSAGE_SHORT_PASSWORD = "Password must be at least 7 characters."
    MESSAGE_INVALID_EMAIL = "Invalid email pattern."

    GITHUB_EMAIL_DOMAIN = "@github.com"

class LoginConst:
    FIELD_EMAIL = "email"
    FIELD_PASSWORD = "password"

    MESSAGE_LOGIN_SUCCESS = "Logged in successfully"
    MESSAGE_INCORRECT_PASSWORD = "Incorrect password. Try again."
    MESSAGE_NONEXIST_EMAIL = "Email does not exist. Try again"
    MESSAGE_CORRUPT_DATABASE = "Contact database is corrupted. Please contact admin for support."

class UserInfo:
    def __init__(self, login_id: str, email: str, is_sso: bool) -> None:
        self.login_id = login_id
        self.email = email
        self.is_sso = is_sso

    def to_dict(self):
        return {
            "login_id": self.login_id,
            "email": self.email,
            "is_sso": self.is_sso
        }


# Private functions

def _is_valid_email(email: str):
    email_pattern = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    match = email_pattern.match(email)
    return bool(match)

def _get_username_from_email(email: str):
    if _is_valid_email(email):
        match = re.match(r'^([^@]+)@', email)
        if match:
            return match.group(1)
    return None

def _get_github_oauth():
    oauth = OAuth(current_app)
    github = oauth.register(
        name="github",
        client_id=current_app.config[AppConst.CONFIG_GITHUB_CLIENT_ID],
        client_secret=current_app.config[AppConst.CONFIG_GITHUB_CLIENT_SECRET],
        request_token_params=None,
        base_url='https://api.github.com/',
        request_token_url=None,
        access_token_method='POST',
        access_token_url='https://github.com/login/oauth/access_token',
        authorize_url='https://github.com/login/oauth/authorize',
    )
    return github
