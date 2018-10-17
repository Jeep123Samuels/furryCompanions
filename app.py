"""App script for furryCompanions."""

import logging

from flask import Flask
from flask_restful import Api
from flask_sqlalchemy import SQLAlchemy
from pymemcache.client import base
from webargs.flaskparser import abort, parser

from config import APP_PORT, FLASK_ENV, app_config

name = 'Furry Companion Service'

logger = logging.getLogger(name)

app = Flask(name)
app_api = Api(app=app)

app.config.from_object(app_config[FLASK_ENV])

db = SQLAlchemy(app)

memcache_client = base.Client(('localhost', 11211))


@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


def start_resources():
    from api import CreateListDog, DeleteGetDog, UpdateDog

    app_api.add_resource(CreateListDog, '/dog/', endpoint='dog')
    app_api.add_resource(DeleteGetDog, '/dog/<int:dog_id>/', endpoint='target_dog')
    app_api.add_resource(UpdateDog, '/dog_update/', endpoint='target_dog_update')


@parser.error_handler
def handle_request_parsing_error(err, req, schema):
    """webargs error handler that uses Flask-RESTful's abort function to return
    a JSON error response to the client.
    """
    abort(422, errors=err.messages)


if __name__ == '__main__':
    start_resources()
    logging.basicConfig(level=logging.DEBUG)
    app.run(host='0.0.0.0', port=APP_PORT, debug=True)
