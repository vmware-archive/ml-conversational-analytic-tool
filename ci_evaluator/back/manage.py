from flask.cli import FlaskGroup
from flaskr import app
from flaskr.models import db

cli = FlaskGroup(app)


@cli.command("create_db")
def create_db():
    db.drop_all()
    db.create_all()
    db.session.commit()
    print('Done\n')

@cli.command("migrate")
def migrate():
    db.create_all()
    db.session.commit()
    print('Done\n')
    

if __name__ == "__main__":
    cli()
