from flaskr.models import db


class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text)
    start_year = db.Column(db.Integer)
    end_year = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=db.func.now())

