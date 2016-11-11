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


class TestShifts(BaseTest, TestCase):

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

    def test_create_single_shift_no_repeating_key_JSON(self):
        """
        Tests creating a single shift with no repitition
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00',
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                }

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 1

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

        # print new_shifts[0].start_time
        assert new_shifts[0].start_time == '2016-10-26T08:00:00'
        assert new_shifts[0].end_time == '2016-10-26T09:00:00'

    def test_create_single_shift_empty_repeating_key_JSON(self):
        """
        Tests when an empty repeating list is given to the create shift function
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00',
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                'repeating': []
                }

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 1

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

        # print new_shifts[0].start_time
        assert new_shifts[0].start_time == '2016-10-26T08:00:00'
        assert new_shifts[0].end_time == '2016-10-26T09:00:00'


    def test_create_single_shift_null_repeating_key_JSON(self):
        """
        Tests when an nonetype repeating key is given to the create shift function
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00',
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                'repeating': None
                }

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 1

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

        # print new_shifts[0].start_time
        assert new_shifts[0].start_time == '2016-10-26T08:00:00'
        assert new_shifts[0].end_time == '2016-10-26T09:00:00'


    def test_create_single_shift_not_assigned(self):
        """
        Tests creating a single shift with no repitition
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': None,
                'start_time': '2016-10-26T08:00:00',
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                }

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 1

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

        # print new_shifts[0].start_time
        assert new_shifts[0].start_time == '2016-10-26T08:00:00'
        assert new_shifts[0].end_time == '2016-10-26T09:00:00'


    def test_create_repeating_shifts_same_day_in_repeating_JSON(self):
        """
        Tests creating a new shift from
        a dictionary (or JSON)
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00',    # base day is Wed, day_int = 2
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                'repeating': [1, 2]}                    # day_int 2 in 'repeating'

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 8     # 4 shifts per day (base day, all repeating days)

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

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
        
    def test_create_repeating_shifts_diff_days_in_repeating_JSON(self):
        """
        Tests creating a new shift from
        a dictionary (or JSON)
        :return:
        """
        pos = org_utils.get_position(1)
        shift_dict = {'position_id': pos.id,
                'assigned_user_id': self.john.id,
                'start_time': '2016-10-26T08:00:00',    # base day is Wed, day_int = 2
                'end_time': '2016-10-26T09:00:00',
                'description': 'desc',
                'repeating': [1, 3]}                    # day_int = 2 not present

        new_shifts = org_utils.create_shifts_JSON(shift_dict)
        new_shifts.sort(key=lambda shift: shift.start_time) # sort list by start_time

        assert new_shifts is not None
        # print len(new_shifts)
        assert len(new_shifts) == 9     # 1 shift for base day, 
                                        # 4 shifts per day in 'repeating'

        for s in new_shifts:
            assert s.position_id == shift_dict['position_id']
            assert s.assigned_user_id == shift_dict['assigned_user_id']
            assert s.description == shift_dict['description']

        assert new_shifts[0].start_time == '2016-10-25T08:00:00'
        assert new_shifts[1].start_time == '2016-10-26T08:00:00'
        assert new_shifts[2].start_time == '2016-10-27T08:00:00'
        assert new_shifts[3].start_time == '2016-11-01T08:00:00'
        assert new_shifts[4].start_time == '2016-11-03T08:00:00'
        assert new_shifts[5].start_time == '2016-11-08T08:00:00'
        assert new_shifts[6].start_time == '2016-11-10T08:00:00'
        assert new_shifts[7].start_time == '2016-11-15T08:00:00'
        assert new_shifts[8].start_time == '2016-11-17T08:00:00'

        assert new_shifts[0].end_time == '2016-10-25T09:00:00'
        assert new_shifts[1].end_time == '2016-10-26T09:00:00'
        assert new_shifts[2].end_time == '2016-10-27T09:00:00'
        assert new_shifts[3].end_time == '2016-11-01T09:00:00'
        assert new_shifts[4].end_time == '2016-11-03T09:00:00'
        assert new_shifts[5].end_time == '2016-11-08T09:00:00'
        assert new_shifts[6].end_time == '2016-11-10T09:00:00'
        assert new_shifts[7].end_time == '2016-11-15T09:00:00'
        assert new_shifts[8].end_time == '2016-11-17T09:00:00'

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
