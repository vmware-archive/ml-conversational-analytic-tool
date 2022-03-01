import re, requests
from flask import Blueprint
from flask import render_template
from flask import request
from flaskr import db, app
from flaskr.extract.graph_ql_request import MyQuery


gr = MyQuery()

bp = Blueprint("evaluation", __name__, url_prefix="/eval")

@bp.route("/evaluate", methods=["GET"])
def evaluate():
    
    return render_template("evaluation/evaluate.html")

@bp.route("/project_request", methods=["POST"])
def project_request():
    req = request.form

    missing = list()
    for k, v in req.items():
        if k == 'project_year':
            continue
        if v == "":
            missing.append(k)
    if missing:
        feedback = f"Missing progect's link. \n"
        feedback += "If you want to evaluate a project, "
        feedback += "please provide a GitHub link to it."
        return render_template("evaluation/evaluate.html", feedback=feedback)
    link = req['project_link']
    year_str = req['project_year']
    if year_str:
        year = year_str.strip()
    else:
        year = 2021

    if not re.match("\d{4}", year):
        feedback = f"Provided year is not correct, please type 4 digit year."
        return render_template("evaluation/evaluate.html", feedback=feedback)

    ind_repo = link.rfind("/")
    ind_git = link.rfind(".git")
    ind_github = link.rfind("github.com")
    if (ind_github) == -1:
        feedback = f"Provided link is not a valid github url."
        return render_template("evaluation/evaluate.html", feedback=feedback)
    
    owner = link[ind_github + 11 : ind_repo]
    name = link[ind_repo + 1 : len(link) if ind_git == -1 else ind_git]
    whole_name = owner + "/" + name
    r = gr.run_query(gr.pg_query(owner, name, whole_name, year))

    rj = r.json()
    re_proj_errors = list()
    if 'errors' in rj:
        if isinstance(rj['errors'], list):
            error_dct = rj['errors'][0]
            re_proj_errors.append(error_dct['message'])
            re_proj_errors.append(error_dct['type'])
        return render_template("evaluation/evaluate.html", re_proj_errors=re_proj_errors)


    ml_response = requests.post(
        f'{app.config["ML_SERVICE_URI"]}/api/predict/project',
        json=r.json(),
    )

    return render_template(
        "evaluation/project_request.html", 
        project_link=link, 
        project_year=year, 
        project_prediction=ml_response.json()
    )


@bp.route("/pr_request", methods=["POST"])
def pr_request():
    req = request.form

    missing = list()
    for k, v in req.items():
        if v == '':
            missing.append(k)
    if missing:
        feedback = f"Missing pr's link. \n"
        feedback += "If you want to evaluate a particular pr, "
        feedback += "please provide a GitHub link to it."
        return render_template("evaluation/evaluate.html", feedback=feedback)

    link = req['pr_link']

    ind_repo = link.rfind("/")
    ind_github = link.rfind("github.com")
    ind_pull = link.rfind("pull")

    if (ind_github) == -1:
        feedback = f"Provided link is not a valid github url."
        return render_template("evaluation/evaluate.html", feedback=feedback)
    
    pr_number = link[ind_repo + 1 : len(link)]
    sub_link = link[ind_github + 11 : ind_repo - 5]
    ind_sub = sub_link.rfind("/")
    owner = sub_link[: ind_sub]
    name = sub_link[ind_sub + 1:]
    r = gr.run_query(gr.pr_query(owner, name, pr_number))

    rj = r.json()
    re_errors = list()
    if 'errors' in rj:
        if isinstance(rj['errors'], list):
            error_dct = rj['errors'][0]
            re_errors.append(error_dct['message'])
            re_errors.append(error_dct['type'])
        return render_template("evaluation/evaluate.html", re_errors=re_errors)

    ml_response = requests.post(
        f'{app.config["ML_SERVICE_URI"]}/api/predict/pr', 
        json=r.json()
    )

    resp = ml_response.json()    
    return render_template("evaluation/pr_request.html", pr_link=link, pr_prediction=resp)


@bp.route("/list_projects", methods=["GET", "POST"])
def list_projects():
    """Log in a registered user by adding the user id to the session."""

    return render_template("evaluation/list_projects.html")

@bp.errorhandler(404)
def page_not_found(e):
    return render_template("errors/404.html"), 404
