from flask_testing import TestCase

from project import app, db
from project.models import User, Organization, Membership, Position, Shift
import project.utils.organization as org_utils
# from project.utils.organization import create_organization, get_organization


class TestOrganization(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        user = User(
            email='owner@organization.com',
            first_name='Organization',
            last_name='Owner',
            password='password',
            confirmed=True
        )
        db.session.add(user)
        db.session.commit()

        org = Organization('Test', user.id)

        db.session.add(org)
        db.session.commit()

        john = User(
            email='member@organization.com',
            first_name='John',
            last_name='Doe',
            password='password',
            confirmed=True
        )

        db.session.add(john)
        db.session.commit()

        john_membership = Membership(
            member_id=john.id,
            organization_id=org.id,
            is_owner=False,
            joined=True
        )

        db.session.add(john_membership)
        db.session.commit()

        position = Position(
            title='Test Position',
            organization_id=org.id
        )

        db.session.add(position)
        db.session.commit()

        self.owner = user
        self.john = john
        self.john_membership = john_membership
        self.organization = org
        self.position = position

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_get_organization(self):
        """
        Tests Getting an organization by ID
        :return:
        """

        org = org_utils.get_organization(1)
        print org.name
        assert org.id == 1
        assert org.owner_id == 1
        assert org.name == 'Test'

        org = org_utils.get_organization(2)
        assert org is None

    def test_get_position(self):
        """
        Tests getting a position by ID
        :return:
        """
        


    def test_create_organization(self):
        """
        Tests creating a new organization and assigning it an owner
        :return:
        """

        organization, membership = org_utils.create_organization(name='Test-Org', owner_id=self.owner.id)

        assert organization.name == 'Test-Org'
        assert organization.owner_id == self.owner.id
        assert membership.member_id == self.owner.id
        assert membership.organization_id == organization.id
        assert membership.joined == True
        assert membership.is_owner == True
