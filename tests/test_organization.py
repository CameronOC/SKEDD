from flask_testing import TestCase

from source import app, db
from source.models import User, Organization, Membership
from source.utils.organization import create_organization


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

    def test_create_organization(self):
        """
        Tests creating a new organization and assigning it an owner
        :return:
        """
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

        assert organization.name == 'Test-Org'
        assert organization.owner_id == owner.id
        assert membership.member_id == owner.id
        assert membership.organization_id == organization.id
        assert membership.joined == True
        assert membership.is_owner == True

if __name__ == '__main__':
    unittest.main()