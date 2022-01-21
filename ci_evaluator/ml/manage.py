from flask.cli import FlaskGroup
from service import app
from service import constants as cs

cli = FlaskGroup(app)


@cli.command("train")
def train():
    from service.ml_models import train_models
    train_models.train(cs.FILENAMES, cs.CSV)
    print('Done\n')


if __name__ == "__main__":
    cli()
