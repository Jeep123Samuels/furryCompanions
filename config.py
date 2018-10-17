import os

from dotenv import load_dotenv

dotenv_path = '.env'
load_dotenv(dotenv_path)

FLASK_ENV = os.getenv('FLASK_ENV', 'development')
APP_PORT = os.getenv('APP_PORT', 5000)


class Config(object):
    """Parent configuration class."""
    DEBUG = False
    CSRF_ENABLED = True
    SECRET = os.getenv('SECRET')
    FLASK_ENV = FLASK_ENV

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.getenv('SECRET_KEY')

    # Memcache Settings
    MEMCACHE_TIMEOUT = int(os.getenv('MEMCACHE_TIMEOUT', 60))


class DevelopmentConfig(Config):
    """Configurations for Development."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv('DEV_DATABASE_URL')


class TestingConfig(Config):
    """Configurations for Testing, with a separate test database."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv('TESTING_DATABASE_URL')
    DEBUG = False


class ProductionConfig(Config):
    """Configurations for Production."""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}
