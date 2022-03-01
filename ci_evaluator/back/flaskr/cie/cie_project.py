from flask import Blueprint
from flask import render_template

# from flaskr import db

bp = Blueprint("cie_project", __name__)

@bp.route("/about")
def about():
    """Clear the current session, including the stored user id."""
    return render_template("cie_project/about.html")


@bp.route("/")
def index():
    """Clear the current session, including the stored user id."""
    return render_template("cie_project/index.html")

@bp.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
