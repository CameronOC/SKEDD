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

class MembershipToDictTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_nonetype(self):
        """
        tests converting a NoneType object
        :return:
        """
        assert org_utils.membership_to_dict(None) is None

    def test_invalid_type(self):
        """
        Tets converting an object that isn't a membership
        :return:
        """
        shift = Shift(assigned_user_id=1, description='', position_id=1,
                             start_time='2007-04-05T14:30', end_time='2007-04-05T14:30')

        self.assertRaises(TypeError, org_utils.membership_to_dict, shift)

    def test_valid(self):
        """
        tests with a valid membership
        :return:
        """
        membership = Membership(member_id=1, organization_id=1, is_admin=True, is_owner=False, joined=True)
        assert membership is not None
        membership_dict = org_utils.membership_to_dict(membership)

        assert membership_dict is not None

        assert 'id' in membership_dict
        assert membership_dict['id'] == membership.id

        assert 'member_id' in membership_dict
        assert membership_dict['member_id'] == membership.member_id

        assert 'organization_id' in membership_dict
        assert membership_dict['organization_id'] == membership.organization_id

        assert 'is_owner' in membership_dict
        assert membership_dict['is_owner'] == False

        assert 'is_admin' in membership_dict
        assert membership_dict['is_admin'] == True

        assert 'joined' in membership_dict
        assert membership_dict['joined'] == True


class ShiftToDictTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_nonetype(self):
        """
        tests converting a NoneType object
        :return:
        """
        assert org_utils.shift_to_dict(None) is None

    def test_invalid_type(self):
        """
        Tets converting an object that isn't a membership
        :return:
        """
        membership = Membership(member_id=1, organization_id=1, is_admin=True, is_owner=False, joined=True)

        self.assertRaises(TypeError, org_utils.shift_to_dict, membership)

    def test_valid_none_missing(self):
        """
        Tests a valid dictionary where all fields are filled
        :return:
        """
        position = Position(
            title='Test Position',
            organization_id=1,
            description='test'
        )

        user = User(
            email='member@organization.com',
            first_name='John',
            last_name='Doe',
            password='password',
            confirmed=True
        )

        shift = Shift(assigned_user_id=user.id, description='', position_id=position.id,
                      start_time='2007-04-05T14:30', end_time='2007-04-05T14:30')

        shift.Position = position
        shift.user = user

        assert shift is not None

        shift_dict = org_utils.shift_to_dict(shift)
        assert shift_dict is not None

        assert 'id' in shift_dict
        assert shift_dict['id'] == shift.id

        assert 'position_id' in shift_dict
        assert shift_dict['position_id'] == shift.Position.id

        assert 'position_title' in shift_dict
        assert shift_dict['position_title'] == shift.Position.title

        assert 'start' in shift_dict
        assert shift_dict['start'] == shift.start_time

        assert 'end' in shift_dict
        assert shift_dict['end'] == shift.end_time

        assert 'description' in shift_dict
        assert shift_dict['description'] == shift.description

        assert 'assigned_member_id' in shift_dict
        assert shift_dict['assigned_member_id'] == shift.assigned_user_id

        assert 'assigned_member' in shift_dict
        assert shift_dict['assigned_member'] == shift.user.first_name + ' ' + shift.user.last_name

    def test_valid_description_missing(self):
        """
        Tests a valid dictionary where the description is missing
        :return:
        """
        position = Position(
            title='Test Position',
            organization_id=1,
            description='test'
        )

        user = User(
            email='member@organization.com',
            first_name='John',
            last_name='Doe',
            password='password',
            confirmed=True
        )

        shift = Shift(assigned_user_id=user.id, description=None, position_id=position.id,
                             start_time='2007-04-05T14:30', end_time='2007-04-05T14:30')

        shift.Position = position
        shift.user = user

        assert shift is not None

        shift_dict = org_utils.shift_to_dict(shift)
        assert shift_dict is not None

        assert 'id' in shift_dict
        assert shift_dict['id'] == shift.id

        assert 'position_id' in shift_dict
        assert shift_dict['position_id'] == shift.Position.id

        assert 'position_title' in shift_dict
        assert shift_dict['position_title'] == shift.Position.title

        assert 'start' in shift_dict
        assert shift_dict['start'] == shift.start_time

        assert 'end' in shift_dict
        assert shift_dict['end'] == shift.end_time

        assert 'description' in shift_dict
        assert shift_dict['description'] == ''

        assert 'assigned_member_id' in shift_dict
        assert shift_dict['assigned_member_id'] == shift.assigned_user_id

        assert 'assigned_member' in shift_dict
        assert shift_dict['assigned_member'] == shift.user.first_name + ' ' + shift.user.last_name

    def test_valid_user_missing(self):
        """
        Tests a valid dictionary where no user is assigned
        :return:
        """
        position = Position(
            title='Test Position',
            organization_id=1,
            description='test'
        )

        shift = Shift(assigned_user_id=None, description='A description', position_id=position.id,
                             start_time='2007-04-05T14:30', end_time='2007-04-05T14:30')

        shift.Position = position

        assert shift is not None

        shift_dict = org_utils.shift_to_dict(shift)
        assert shift_dict is not None

        assert 'id' in shift_dict
        assert shift_dict['id'] == shift.id

        assert 'position_id' in shift_dict
        assert shift_dict['position_id'] == shift.Position.id

        assert 'position_title' in shift_dict
        assert shift_dict['position_title'] == shift.Position.title

        assert 'start' in shift_dict
        assert shift_dict['start'] == shift.start_time

        assert 'end' in shift_dict
        assert shift_dict['end'] == shift.end_time

        assert 'description' in shift_dict
        assert shift_dict['description'] == shift.description

        assert 'assigned_member_id' in shift_dict
        assert shift_dict['assigned_member_id'] == 0

        assert 'assigned_member' in shift_dict
        assert shift_dict['assigned_member'] == 'Unassigned'