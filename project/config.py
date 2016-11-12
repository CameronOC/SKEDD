# source/config.py

import os
import psycopg2
import urlparse
basedir = os.path.abspath(os.path.dirname(__file__))


class BaseConfig(object):
    """Base configuration."""
    DEBUG = False
    BCRYPT_LOG_ROUNDS = 13
    WTF_CSRF_ENABLED = True
    DEBUG_TB_ENABLED = False
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    SECRET_KEY = 'my_precious'
    SECURITY_PASSWORD_SALT = 'my_precious_two'

    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True

    MAIL_USERNAME = os.environ['APP_MAIL_USERNAME']
    MAIL_PASSWORD = os.environ['APP_MAIL_PASSWORD']

    MAIL_DEFAULT_SENDER = 'from@example.com'


class DevelopmentConfig(BaseConfig):
    """Development configuration."""
    DEBUG = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'dev.sqlite')
    DEBUG_TB_ENABLED = True


class TestingConfig(BaseConfig):
    """Testing configuration."""
    TESTING = True
    DEBUG = True
    BCRYPT_LOG_ROUNDS = 1
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'test.sqlite')


class ProductionConfig(BaseConfig):
    DATABASE_URL = "postgres://qwewadszqdekje:7IQa5Oi2Nw6UF5VFjCYkcpReWp@ec2-54-243-203-85.compute-1.amazonaws.com:5432/dcoknfoqnds1l3"
    urlparse.uses_netloc.append("postgres")
    url = urlparse.urlparse(os.environ["DATABASE_URL"])

    conn = psycopg2.connect(
        database=url.path[1:],
        user=url.username,
        password=url.password,
        host=url.hostname,
        port=url.port
    )
