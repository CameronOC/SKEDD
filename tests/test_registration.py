from flask_testing import TestCase

from source import app, db
from source.models import User


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        user = User(email="ad@min.com", password="admin_user", first_name='local', last_name='admin')
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()