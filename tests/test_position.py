from flask_testing import TestCase, utils
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils
from base_test import BaseTest
#from project.utils.organization import deletepositions
# from project.utils.organization import create_organization, get_organization
import datetime
import json


class TestPosition(BaseTest, TestCase):

    def test_assign_member_to_position(self):
        """
        Tests that a user is assigned to a position
        :return:
        """
        pos = org_utils.get_position(1).id
        user = org_utils.get_user(1).id
        
        org_utils.assign_member_to_position(user, pos)
        assigneduser = position_assignments.select(position_assignments.c.user_id == 1)
        assert assigneduser is not None

    def test_unassign_member_to_position(self):
        """
        Tests that a user is unassigned from a position
        :return:
        """
        pos = org_utils.get_position(1).id
        user = org_utils.get_user(1).id

        org_utils.assign_member_to_position(user, pos)
        org_utils.unassign_member_to_position(user, pos)
        unassigned = position_assignments.select(position_assignments.c.user_id == 1)
        assert unassigned is not None

    def test_get_postion(self):
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

    def test_create_position(self):
        """
        Tests that a position is delete from a organization
        :return:
        """
        pos = org_utils.get_position(1)
        org = org_utils.get_organization(1)
        assert pos is not None

    def test_delete_position(self):
        """
        Tests that a position is delete from a organization
        :return:
        """
        pos = org_utils.get_position(1).id
        assert pos is not None

        org_utils.deletepositions(pos)
        pos2 = org_utils.get_position(1)
        assert pos2 is None

    def test_get_all_positions_JSON(self):
        """
        Tests getting all shifts as a JSON
        object
        :return:
        """
        positions = org_utils.get_positions_for_org_JSON(org_id=1) #string
        positions_list = json.loads(positions) # dictionary of dictionaries

        assert positions is not None
        assert positions_list is not None
        assert len(positions_list) == 1
        for p in positions_list:
            assert p['title'] == self.position.title
            assert p['organization_id'] == self.position.organization_id

    def test_get_members_for_position(self):
        """
        Tests getting all the users for a specific position
        :return:
        """
        org_utils.assign_member_to_position(self.john.id, self.position.id)
        org_utils.assign_member_to_position(self.owner.id, self.position.id)

        response = json.loads(org_utils.get_members_for_position(self.position.id))
        assert response is not None
        assert 'status' in response
        assert response['status'] == 'success'

        assert 'members' in response
        members = response['members']

        print members
        assert len(members) == 2
        member_one = members[0]
        member_two = members[1]

        assert member_one['first_name'] == 'John'
        assert member_one['last_name'] == 'Doe'
        assert member_one['id'] == 2

        assert member_two['first_name'] == 'Organization'
        assert member_two['last_name'] == 'Owner'
        assert member_two['id'] == 1

    def test_get_users_for_position(self):
        """
        Tests getting all the users for a specific position
        :return:
        """
        org_utils.assign_member_to_position(self.john.id, self.position.id)
        org_utils.assign_member_to_position(self.owner.id, self.position.id)

        response = json.loads(org_utils.get_users_for_position(self.position.id))

        assert response is not None
        assert len(response) == 2

        member_one = response[0]
        member_two = response[1]

        assert member_one['first_name'] == 'John'
        assert member_one['last_name'] == 'Doe'
        assert member_one['id'] == 2

        assert member_two['first_name'] == 'Organization'
        assert member_two['last_name'] == 'Owner'
        assert member_two['id'] == 1

    def test_get_assigned_positions_for_user(self):
        """
        Tests getting all the users for assigned to a position
        :return:
        """

        org_utils.assign_member_to_position(self.john.id, self.position.id)
        response = json.loads(org_utils.get_assigned_positions_for_user(1, 2))
        assert response is not None
