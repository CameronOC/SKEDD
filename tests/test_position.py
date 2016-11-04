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


class TestPosition(BaseTest, TestCase):

    def test_assign_member_to_position(self):
        """
        Tests that a user is assigned to a position
        :return:
        """
        pos = org_utils.get_position(1)
        org = org_utils.get_organization(1)
        user = User(
            email='member2@organization.com',
            first_name='Will',
            last_name='Smith',
            password='password',
            confirmed=True
        )
        org_utils.assign_member_to_position(user, pos, org)
        assigneduser = position_assignments.select(position_assignments.c.user_id == 2)
        assert assigneduser is not None

    def test_unassign_member_to_position(self):
        """
        Tests that a user is unassigned from a position
        :return:
        """

    def test_delete_position(self):
        """
        Tests that a position is delete from a organization
        :return:
        """
        pos = org_utils.get_position(1)
        org = org_utils.get_organization(1)
        assert pos is not None

        org_utils.deletepositions(pos, org)

        pos2 = org_utils.get_position(1)
        assert pos2 is None
