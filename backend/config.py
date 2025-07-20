from os import path
import platform

basedir = path.abspath(path.dirname(__file__))
DB_PATH=path.abspath(path.join(path.dirname(__file__), path.join('data', 'deduction_games_old.db')))
ostype = platform.system


class Config:
    """Flask Base config."""
    STATIC_FOLDER = 'static'
    TEMPLATES_FOLDER = 'templates'


class ProdConfig(Config):
    """Production configuration"""
    FLASK_ENV = 'production'
    DEBUG = False
    TESTING = False
    if ostype in ['Linux', 'MacOs' ]:
        SQLALCHEMY_DATABASE_URI = f"sqlite:////{DB_PATH}"
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"


class DevConfig(Config):
    """DEV only config"""
    FLASK_ENV = 'development'
    DEBUG = True
    TESTING = True
    if ostype in ['Linux', 'MacOs' ]:
        SQLALCHEMY_DATABASE_URI = f"sqlite:////{DB_PATH}"
    else:
        SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH}"
    #Print database-related actions to console.
    SQLALCHEMY_ECHO = False
