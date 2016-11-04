from flask_testing import TestCase
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils
from base_test import BaseTest
#from project.utils.organization import deletepositions
# from project.utils.organization import create_organization, get_organization
import datetime
import json


class TestOrganization(BaseTest, TestCase):

    def test_get_organization(self):
        """
        Tests Getting an organization by ID
        :return:
        """

        org = org_utils.get_organization(1)
        assert org is not None
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
        position = org_utils.get_position(1)
        assert position is not None
        assert position.id == self.position.id
        assert position.title == self.position.title

        position = org_utils.get_position(3)
        assert position is None


    def test_create_organization(self):
        """
        Tests creating a new organization and assigning it an owner
        :return:
        """
        organization, membership = org_utils.create_organization(name='Test-Org', owner_id=self.owner.id)
        assert organization is not None
        assert membership is not None
        assert organization.name == 'Test-Org'
        assert organization.owner_id == self.owner.id
        assert membership.member_id == self.owner.id
        assert membership.organization_id == organization.id
        assert membership.joined == True
        assert membership.is_owner == True


    def test_invite__unconfirmed_user(self):
        """
        Test sending an invite to join an organization to a user that has not already
        created an account
        :return:
        """
        membership = org_utils.invite_member(self.organization, 'invitee@org.com', 'Alice', 'Green')

        assert membership is not None

        user = membership.member
        org = membership.organization

        assert user is not None
        assert org is not None

        assert membership.joined == False

        assert user.email == 'invitee@org.com'
        assert user.first_name == 'Alice'
        assert user.last_name == 'Green'
        assert user.confirmed == False

        assert org.id == self.organization.id
        assert org.name == self.organization.name
        assert org.owner_id == self.organization.owner_id

    def test_invite_confirmed_user(self):
        """
        Tests inviting a user that already has a SKEDD account to an organization
        :return:
        """
        confirmed_user = User(email='confirmed@user.com',
                              password='password',
                              confirmed=True,
                              first_name='John',
                              last_name='Doe')
        db.session.add(confirmed_user)
        db.session.commit()

        membership = org_utils.invite_member(self.organization, 'confirmed@user.com', 'John', 'Doe')

        assert membership is not None

        user = membership.member
        org = membership.organization

        assert user is not None
        assert org is not None

        assert membership.joined == False

        assert user.email == 'confirmed@user.com'
        assert user.first_name == 'John'
        assert user.last_name == 'Doe'
        assert user.confirmed == True

        assert org.id == self.organization.id
        assert org.name == self.organization.name
        assert org.owner_id == self.organization.owner_id

    def test_invite_joined_user(self):
        """
        Tests trying to invite user that is already part of the organization.
        Should no create a new membership entry
        :return:
        """

        membership = org_utils.invite_member(self.organization,
                                             self.john.email,
                                             self.john.first_name,
                                             self.john.last_name)

        memberships = Membership.query.filter_by(organization=self.organization, member=self.john).all()

        assert memberships is not None

        assert len(memberships) == 1

    def test_join(self):
        """
        Tests marking a previously unconfirmed user as having joined an organization
        :return:
        """
        self.john_membership.joined = False
        db.session.commit()
        g.user = None

        membership = org_utils.confirm_invite(self.john_membership)

        assert membership is not None
        assert membership.is_owner == False
        assert membership.joined
