from flask_testing import TestCase
from project import app, db
import project.utils.utils as utils
import project.forms as forms


class MergeDictionariesTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_two_dicts(self):
        dict1 = {'key': 1, 'key2': 2}
        dict2 = {'key3': 3, 'key4': 4}

        dict_result = utils.merge_dicts(dict1, dict2)

        assert 'key' in dict_result
        assert dict_result['key'] == 1

        assert 'key2' in dict_result
        assert dict_result['key2'] == 2

        assert 'key3' in dict_result
        assert dict_result['key3'] == 3

        assert 'key4' in dict_result
        assert dict_result['key4'] == 4


class ShiftValidationTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_correct(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with correct input
        :return:
        """
        # test with correct input
        form = {'shift_position_id': '1', 'shift_assigned_member_id': '2'}
        assert 'status' not in utils.validate_shift(form)

    def test_no_pos(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        without position id
        :return:
        """
        form = {'shift_assigned_member_id': '2'}
        assert 'status' not in utils.validate_shift(form)

    def test_required_pos_missing(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        without position id with position id required
        :return:
        """
        form = {'shift_assigned_member_id': '2'}
        return_dict = utils.validate_shift(form, pos_required=True)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

    def test_no_member_id(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        without member id
        :return:
        """
        form = {'shift_position_id': '1'}
        assert 'status' not in utils.validate_shift(form)

    def test_no_entries(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        without either position or member ids
        :return:
        """
        form = {}
        assert 'status' not in utils.validate_shift(form)

    def test_pos_zero(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with '0' for position id
        :return:
        """
        form = {'shift_position_id': '0', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_shift(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

    def test_pos_neg(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with a negative number for position id
        :return:
        """
        form = {'shift_position_id': '-123', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_shift(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

    def test_pos_float(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with a float for position id
        :return:
        """
        form = {'shift_position_id': '.123', 'shift_assigned_member_id': '1'}
        return_dict = utils.validate_shift(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' in return_dict['errors'] and \
               'Invalid Member id: ' not in return_dict['errors']

    def test_mem_neg(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with a negative number for member id
        :return:
        """
        form = {'shift_assigned_member_id': '-234'}
        return_dict = utils.validate_shift(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' not in return_dict['errors'] and \
               'Invalid Member id: ' in return_dict['errors']

    def test_mem_float(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with a float for member id
        :return:
        """
        form = {'shift_assigned_member_id': '.123'}
        return_dict = utils.validate_shift(form)
        print return_dict
        assert 'status' in return_dict and \
               'Invalid Position id: ' not in return_dict['errors'] and \
               'Invalid Member id: ' in return_dict['errors']

    def test_mem_zero(self):
        """
        Tests the function that verifies the member and position IDs from the shift form
        with '0' for member id
        :return:
        """
        # test
        form = {'shift_assigned_member_id': '0'}
        assert 'status' not in utils.validate_shift(form)


class ShiftFormErrorsTest(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_valid(self):
        """
        # test a valid shift form
        :param form:
        :return:
        """
        form = forms.ShiftForm(shift_description='A description',
                               shift_repeating=True,
                               shift_repeat_list=['1', '2'],
                               shift_start_time='2007-04-05T14:30',
                               shift_end_time='2007-04-05T14:30',
                               shift_id='1')

        assert form.validate()
        errors_dict = utils.shift_form_errors_to_dict(form)
        for key, value in errors_dict.iteritems():
            assert len(value) == 0

    def test_invalid_description(self):
        """
        # test a valid shift form
        :param form:
        :return:
        """

        description = 'bTMhyNFpvAVclfxosYtAzVhUsrs67OLUGjz5oHtm' \
                      'Ge3JomhmHh25tGKbwP3n95oe9ZNL0YgiXb17okJlihQsEJ962Bz1SkRWUV7Rl'

        form = forms.ShiftForm(shift_description=description,
                               shift_repeating=True,
                               shift_repeat_list=['0', '1', '2', '3', '4', '5', '6'],
                               shift_start_time='2007-04-05T14:30',
                               shift_end_time='2007-04-05T14:30',
                               shift_id='1')

        assert not form.validate()
        errors_dict = utils.shift_form_errors_to_dict(form)
        for key, value in errors_dict.iteritems():
            if key == 'Description':
                assert len(value) == 1
            else:
                assert len(value) == 0

    def test_invalid_repeat_list(self):
        shift_repeat_list = ['-1', '7']

        form = forms.ShiftForm(shift_description='A description',
                               shift_repeating=False,
                               shift_repeat_list=shift_repeat_list,
                               shift_start_time='2007-04-05T14:30',
                               shift_end_time='2007-04-05T14:30',
                               shift_id='1')

        assert not form.validate()
        errors_dict = utils.shift_form_errors_to_dict(form)
        for key, value in errors_dict.iteritems():
            if key == 'Day Selector':
                print value
                assert len(value) == 1
            else:
                assert len(value) == 0

