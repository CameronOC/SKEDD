from flask_testing import TestCase

from project import app, db
from project.models import Position


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        position = Position(title="position", organization_id="1")
        db.session.add(position)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()