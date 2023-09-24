from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db, AppConst

jobs = Blueprint("jobs", __name__)

@jobs.route("/jobs")
@login_required
def jobs_explore():
    return render_template("jobs.html", user=current_user)