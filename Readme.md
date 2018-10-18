Furry Companions:
An API CRUD service for I/O functionality for capturing data for dogs

Make sure to install following with apt-get install:
memcached
virtualenv

Then:
    >> pip3 install -r requirements.

add .env:
SECRET="a-long-string-of-random-characters-CHANGE-TO-YOUR-LIKING"
DEV_DATABASE_URL="sqlite:///furry.sqlite3"
FLASK_ENV="development"

TESTING_DATABASE_URL="sqlite:///test_furry.sqlite3"
MEMCACHE_TIMEOUT="60"

Then:
    >> python3 manage.py db migrate
    >> python3 manage.py db upgrade

Remember to switch FLASK_ENV to 'testing'.

To run tests:
    >> pytest
To target specific tests:
    >> pytest -k <test.node.name>

Checking codestyle:
    >> flake8

run app with:
    >> python3 app.py
