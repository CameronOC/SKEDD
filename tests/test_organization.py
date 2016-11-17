from flask_testing import TestCase
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils
from base_test import BaseTest
import project.forms as forms
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
        response_dict = org_utils.invite_member(self.organization, 'invitee@org.com', 'Alice', 'Green')
        assert 'status' in response_dict
        assert response_dict['status'] == 'success'

        assert 'membership' in response_dict
        membership_dict = response_dict['membership']

        user = User.query.filter_by(email='invitee@org.com').first()
        assert user is not None

        assert 'member_id' in membership_dict
        assert 'organization_id' in membership_dict

        assert membership_dict['joined'] == False

        assert membership_dict['organization_id'] == self.organization.id
        assert membership_dict['member_id'] == user.id

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

        response_dict = org_utils.invite_member(self.organization, 'confirmed@user.com', 'John', 'Doe')
        assert 'status' in response_dict
        assert response_dict['status'] == 'success'

        assert 'membership' in response_dict
        membership_dict = response_dict['membership']

        user = User.query.filter_by(email='confirmed@user.com').first()
        assert user is not None

        assert 'member_id' in membership_dict
        assert 'organization_id' in membership_dict

        assert membership_dict['joined'] == False

        assert membership_dict['organization_id'] == self.organization.id
        assert membership_dict['member_id'] == user.id


    def test_invite_joined_user(self):
        """
        Tests trying to invite user that is already part of the organization.
        Should no create a new membership entry
        :return:
        """

        response_dict = org_utils.invite_member(self.organization,
                                             self.john.email,
                                             self.john.first_name,
                                             self.john.last_name)

        assert 'status' in response_dict
        assert response_dict['status'] == 'error'

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
