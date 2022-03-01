from flaskr import app
from flaskr.models import Project


@app.route("/api/get_all", methods=['GET'])
def ci():
    projects = Project.query.evaluated()

    projects = projects.all

    response = {
        'name': 'CI Evaluation projects',
        'projects': [
            {
                'name': str(project.name)
            }
            for project in projects
        ]
    }

    return response
    
