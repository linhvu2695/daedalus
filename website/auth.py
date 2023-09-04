from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import Contact
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user

auth = Blueprint("auth", __name__)

@auth.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
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
        else:
            # add to db
            new_contact = Contact(
                email=email, first_name=firstname, last_name=lastname, 
                password=generate_password_hash(password, method="sha256"))
            db.session.add(new_contact)
            db.session.commit()
            
            login_user(new_contact, remember=True)
            flash(RegisterConst.MESSAGE_ACCOUNT_CREATED, category="success")
            return redirect(url_for("views.home"))

    return render_template("register.html", user=current_user)


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

class LoginConst:
    FIELD_EMAIL = "email"
    FIELD_PASSWORD = "password"

    MESSAGE_LOGIN_SUCCESS = "Logged in successfully"
    MESSAGE_INCORRECT_PASSWORD = "Incorrect password. Try again."
    MESSAGE_NONEXIST_EMAIL = "Email does not exist. Try again"
