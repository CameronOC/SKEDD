from flask_testing import TestCase
from flask import g
from project import app, db
from project.models import User, Organization, Membership, Position, Shift, position_assignments
import project.utils.organization as org_utils
from base_test import BaseTest
import project.forms as forms
import datetime
import json


class TestViews(BaseTest, TestCase):

    def test_landing_page(self):
        rv = self.client.get('/')
        self.assertEqual(rv._status_code, 200, rv._status_code)