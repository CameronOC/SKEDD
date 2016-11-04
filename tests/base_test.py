from flask_testing import TestCase
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils
#from project.utils.organization import deletepositions
# from project.utils.organization import create_organization, get_organization
import datetime
import json


class BaseTest(TestCase):

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
            position_id=position.id,
            assigned_user_id=None,
            start_time='2016-10-26T06:00:00',
            end_time='2016-10-26T07:00:00',
            description=None,
        )

        db.session.add(shift)
        db.session.commit()


        self.owner = user
        self.john = john
        self.john_membership = john_membership
        self.organization = org
        self.position = position
        self.shift = shift

    def tearDown(self):
        db.session.remove()
        db.drop_all()