from flask_testing import TestCase

from project import app, db
from project.models import User
from project.utils.organization import create_organization


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        user = User(email="ad@min.com", password="admin_user", first_name='local', last_name='admin', confirmed=True)
        db.session.add(user)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_position(self):
        owner = User(
            email='owner@organization.com',
            first_name='Organization',
            last_name='Owner',
            password='password',
            confirmed=True
        )
        db.session.add(owner)
        db.session.commit()

        organization, membership = create_organization('Test-Org', owner.id)

        


