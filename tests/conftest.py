"""Global fixtures for app."""

import pytest


from alembic.command import upgrade
from alembic.config import Config
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import app, db
from config import app_config, FLASK_ENV
from models import Dogs

app.config.from_object(app_config[FLASK_ENV])


@pytest.fixture(scope='session')
def app():
    """For some reason this needs to be defined again."""
    from api import CreateListDog, DeleteGetDog, UpdateDog
    from flask import Flask
    from flask_restful import Api
    from config import app_config, FLASK_ENV

    app = Flask('Test Furry Companion Service')
    app.config.from_object(app_config[FLASK_ENV])
    app_api = Api(app=app)

    app_api.add_resource(CreateListDog, '/dog/', endpoint='dog')
    app_api.add_resource(DeleteGetDog, '/dog/<int:dog_id>/', endpoint='target_dog')
    app_api.add_resource(UpdateDog, '/dog_update/', endpoint='target_dog_update')
    return app


@pytest.fixture(scope='session')
def manage(app):
    db.init_app(app)
    Migrate(app, db)
    manager = Manager(app)

    manager.add_command('db', MigrateCommand)

    # run migration command to create tables.
    with app.app_context():
        config = Config('migrations/alembic.ini')
        upgrade(config, 'head')
    db.create_all()
    db.session.commit()


@pytest.fixture
def client(request, manage, app):

    def teardown():
        # clear table after each test.
        db.session.query(Dogs).delete()
        db.session.commit()

    request.addfinalizer(teardown)
    return app.test_client()
