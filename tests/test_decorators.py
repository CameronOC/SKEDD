from flask_testing import TestCase
from base_test import BaseTest
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils

from project.decorators import check_confirmed, owns_organization, organization_member, admin_of_org, shift_belongs_to_org
from project.exceptions import NotOwner, NotMember, ShiftNotInOrg, NotAdmin


@owns_organization
def does_nothing_owns_org(key):
    pass
    
@admin_of_org
def does_nothing_admin(key):
    pass
    
@organization_member
def does_nothing_member_of_org(key):
    pass
    
@shift_belongs_to_org
def does_nothing_shift_belongs(key, key1):
    pass

class TestDecorators(BaseTest, TestCase):
    
    def test_owns_organization(self):
        
        org = org_utils.get_organization(1)
        assert org is not None
        assert org.id == 1
        assert org.owner_id == 1
        assert org.name == 'Test'
        
        member = org_utils.get_user(2) # john
        membership = org_utils.get_membership(org, member)
        assert member is not None
        assert membership is not None
        assert membership.is_owner == False
        
        g.user = org.owner
        does_nothing_owns_org(key=org.id)
        
        g.user = member
        self.assertRaises(NotOwner, does_nothing_owns_org, key=org.id)
        
    def test_admin_of_org(self):
        
        org = org_utils.get_organization(1)
        assert org is not None
        assert org.id == 1
        assert org.owner_id == 1
        assert org.name == 'Test'
        
        john = org_utils.get_user(2) # john
        membership = org_utils.get_membership(org, john)
        assert john is not None
        assert membership is not None
        assert membership.is_admin == False
        membership.change_admin()
        
        jane = User(
            email='member2@organization.com',
            first_name='Jane',
            last_name='Doe',
            password='password',
            confirmed=True
        )
        db.session.add(jane)
        db.session.commit()

        jane_membership = Membership(
            member_id=jane.id,
            organization_id=org.id,
            is_owner=False,
            joined=True
        )
        db.session.add(jane_membership)
        db.session.commit()
        
        g.user = john
        does_nothing_admin(key=org.id)
        
        g.user = jane
        self.assertRaises(NotAdmin, does_nothing_admin, key=org.id)
        
        membership.change_admin() # reset john to non-admin
        
    def test_organization_member(self):
        
        org = org_utils.get_organization(1)
        assert org is not None
        assert org.id == 1
        assert org.owner_id == 1
        assert org.name == 'Test'
        
        john = org_utils.get_user(2) # john
        membership1 = org_utils.get_membership(org, john)
        assert john is not None
        assert membership1 is not None
        
        jane = User(
            email='member2@organization.com',
            first_name='Jane',
            last_name='Doe',
            password='password',
            confirmed=True
        )
        db.session.add(jane)
        db.session.commit()
        
        jane = org_utils.get_user(3) # jane
        membership2 = org_utils.get_membership(org, jane)
        assert jane is not None
        assert membership2 is None
        
        g.user = john
        does_nothing_member_of_org(key=org.id)
        
        g.user = jane
        self.assertRaises(NotMember, does_nothing_member_of_org, key=org.id)
        
    def test_shift_belongs_to_org(self):
        
        org = org_utils.get_organization(1)
        assert org is not None
        assert org.id == 1
        assert org.owner_id == 1
        assert org.name == 'Test'
        
        shift1 = org_utils.get_shift(1)
        assert shift1 is not None
        
        org2 = Organization('Test2', org.owner_id)
        db.session.add(org2)
        db.session.commit()
        
        position = Position(
            title='Test Position',
            organization_id=org2.id,
            description='This is a description'
        )
        db.session.add(position)
        db.session.commit()
        
        shift2 = Shift(
            position_id=position.id,
            assigned_user_id=None,
            start_time='2016-10-26T06:00:00',
            end_time='2016-10-26T07:00:00',
            description=None,
        )
        db.session.add(shift2)
        db.session.commit()
        
        does_nothing_shift_belongs(key=org.id, key1=shift1.id)
        
        self.assertRaises(ShiftNotInOrg, does_nothing_shift_belongs, key=org.id, key1=shift2.id)
        
