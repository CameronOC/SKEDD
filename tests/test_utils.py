from flask_testing import TestCase
from project import app, db
import project.utils.utils as utils

class BaseTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_validate_member_position(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        :return:
        """
        # test with correct input
        form = {'shift_position_id': '1', 'shift_assigned_member_id': '2'}
        assert 'status' not in utils.validate_member_position_id(form)

        # test without position id
        form = {'shift_assigned_member_id': '2'}
        assert 'status' not in utils.validate_member_position_id(form)

        # test without position id with position id required
        form = {'shift_assigned_member_id': '2'}
        return_dict = utils.validate_member_position_id(form, pos_required=True)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

        # test with '0' for position id
        form = {'shift_position_id': '0', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_member_position_id(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

        # test with a negative number for position id
        form = {'shift_position_id': '-123', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_member_position_id(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

        # test with a float for position id
        form = {'shift_position_id': '.123', 'shift_assigned_member_id': '1'}
        return_dict = org_utils.validate_member_position_id(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

        # test with '0' for position id
        form = {'shift_position_id': '0', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_member_position_id(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']