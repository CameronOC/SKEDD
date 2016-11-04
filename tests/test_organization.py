from flask_testing import TestCase
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift
import project.utils.organization as org_utils
# from project.utils.organization import create_organization, get_organization
import datetime
import json


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
        
        shift = Shift(
            position_id = position.id,
            assigned_user_id = None,
            start_time = '2016-10-26T06:00:00',
            end_time = '2016-10-26T07:00:00',
            description = None,
        )
        
        db.session.add(shift)
        db.session.commit

        self.owner = user
        self.john = john
        self.john_membership = john_membership
        self.organization = org
        self.position = position
        self.shift = shift

    def tearDown(self):
        db.session.remove()
        db.drop_all()

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

        position = org_utils.get_position(2)
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
        
    def test_create_shift(self):
        """
        Tests creating a new shift
        :return:
        """
        new_pos = Position(title='Test 2', organization_id=self.organization.id)
        db.session.add(new_pos)
        db.session.commit()
        
        start_time = '2016-10-26T08:00:00'
        end_time = '2016-10-26T09:00:00'
        
        shift = org_utils.create_shift(new_pos.id, self.john.id, start_time, end_time, 'desc')
        
        assert shift is not None
        assert shift.position_id == new_pos.id
        assert shift.assigned_user_id == self.john.id
        assert shift.start_time == start_time
        assert shift.end_time == end_time
        assert shift.description == 'desc'
    
    def test_create_shifts_JSON(self):
        """
        Tests creating a new shift from 
        a dictionary (or JSON)
        :return:
        """
        pos = org_utils.get_position(1)
        dict = {'position_id': pos.id, 
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00', 
                'end_time': '2016-10-26T09:00:00', 
                'description': 'desc',
                'repeating': [1]}
        
        new_shifts = org_utils.create_shifts_JSON(dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time
                
        assert new_shifts is not None
        assert len(new_shifts) == 8     # 4 shifts per day (base day, all repeating days)
        
        for s in new_shifts:
            assert s.position_id == dict['position_id']
            assert s.assigned_user_id == dict['assigned_user_id']
            assert s.description == dict['description']
             
        assert new_shifts[0].start_time == '2016-10-25T08:00:00'
        assert new_shifts[1].start_time == '2016-10-26T08:00:00'
        assert new_shifts[2].start_time == '2016-11-01T08:00:00'
        assert new_shifts[3].start_time == '2016-11-02T08:00:00'
        assert new_shifts[4].start_time == '2016-11-08T08:00:00'
        assert new_shifts[5].start_time == '2016-11-09T08:00:00'
        assert new_shifts[6].start_time == '2016-11-15T08:00:00'
        assert new_shifts[7].start_time == '2016-11-16T08:00:00'
        
        assert new_shifts[0].end_time == '2016-10-25T09:00:00'
        assert new_shifts[1].end_time == '2016-10-26T09:00:00'
        assert new_shifts[2].end_time == '2016-11-01T09:00:00'
        assert new_shifts[3].end_time == '2016-11-02T09:00:00'
        assert new_shifts[4].end_time == '2016-11-08T09:00:00'
        assert new_shifts[5].end_time == '2016-11-09T09:00:00'
        assert new_shifts[6].end_time == '2016-11-15T09:00:00'
        assert new_shifts[7].end_time == '2016-11-16T09:00:00'
        
    def test_get_shift(self):
        """
        Tests getting a shift by ID
        :return:
        """
        shift = org_utils.get_shift(1)
        assert shift is not None
        assert shift.id == self.shift.id
        assert shift.position_id == self.shift.position_id
        assert shift.assigned_user_id == self.shift.assigned_user_id
        assert shift.start_time == self.shift.start_time
        assert shift.end_time == self.shift.end_time
        assert shift.description == self.shift.description
        
        shift = org_utils.get_shift(2)
        assert shift is None
        
    def test_update_shift(self):
        """
        Tests updating a shift
        :return:
        """
        shift = org_utils.get_shift(1)
        
        new_pos = Position(title='Test 3', organization_id=self.organization.id)
        db.session.add(new_pos)
        db.session.commit()
        
        start_time = '2016-10-26T08:00:00'
        end_time = '2016-10-26T10:30:00'

        
        org_utils.update_shift(shift, new_pos.id, self.john.id, 
                                start_time, end_time, 'desc')
        
        # re-query, compare fields
        shift = org_utils.get_shift(1)
        assert shift.position_id == new_pos.id
        assert shift.assigned_user_id == self.john.id
        assert shift.start_time == start_time
        assert shift.end_time == end_time
        assert shift.description == 'desc'
        
        # reset fields for future tests
        org_utils.update_shift(shift, self.shift.position_id, self.shift.assigned_user_id,
                                self.shift.start_time, self.shift.end_time,
                                self.shift.description)
        
    def test_get_all_shifts_JSON(self):
        """
        Tests getting all shifts as a JSON
        object
        :return:
        """
        shifts = org_utils.get_all_shifts_JSON(org_id=1) #string
        shift_dict = json.loads(shifts) # dictionary of dictionaries
        
        assert shifts is not None
        assert shift_dict is not None
        assert len(shift_dict) == 1
        for s in shift_dict:
            assert shift_dict[str(s)]['position_id'] == self.shift.position_id
            assert shift_dict[str(s)]['assigned_user_id'] == self.shift.assigned_user_id
            assert shift_dict[str(s)]['start_time'] == self.shift.start_time
            assert shift_dict[str(s)]['end_time'] == self.shift.end_time
            assert shift_dict[str(s)]['description'] == self.shift.description
