from flaskr.models import db


class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
    score = db.Column(db.Integer)
    year = db.Column(db.Integer)
    calculated_at = db.Column(db.DateTime, default=db.func.now())
    created_at = db.Column(db.DateTime, default=db.func.now())

    project = db.relationship('Project', backref='projects')
