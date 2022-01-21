from flask import Flask, jsonify
from flask.templating import render_template
from flaskr.models import db
from sqlalchemy import select

app = Flask(__name__)
app.config.from_object("flaskr.config.Config")

db.init_app(app)

# apply the blueprints to the app
try:
    from cie import cie_project, evaluation
except Exception as err:
    import traceback
    traceback.print_exc()
    exit(1)

app.register_blueprint(cie_project.bp)
app.register_blueprint(evaluation.bp)

#set path to the home page
app.add_url_rule("/", endpoint="index")

@app.route('/health')
def health():
    return jsonify(
        status='ok', 
        name='health page'
    )


@app.route('/super_secret_admin')
def admin():
    return jsonify(
        status='ok', 
        name='admin page'
    )


@app.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404


try:
    from flaskr.models import *
except Exception as err:
    import traceback
    traceback.print_exc()
    exit(1)
