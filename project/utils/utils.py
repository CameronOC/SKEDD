from random import randint
import datetime
import re

def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def validate_shift(form, pos_required=False):
    """
    validates the member and position ID's from the shift form
    :param form:
    :param pos_required:
    :return:
    """
    return_dict = {}
    errors = False
    if 'shift_position_id' in form:
        if not form['shift_position_id'].isdigit():
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Position id': form['shift_position_id']}
            errors = True
        elif int(form['shift_position_id']) == 0:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Position id': form['shift_position_id']}
            errors = True
    elif pos_required:
        return_dict['status'] = "error"
        return_dict['errors'] = {'Invalid Position id': 'No Position id selected'}
        errors = True

    if 'shift_assigned_member_id' in form:
        if not form['shift_assigned_member_id'].isdigit():
            if errors:
                return_dict['errors']['Invalid Member id'] = form['shift_assigned_member_id']
            else:
                errors = True
                return_dict['status'] = "error"
                return_dict['errors'] = {'Invalid Member id': form['shift_assigned_member_id']}

    if 'shift_description' in form:
        if len(form['shift_description']) < 0 or len(form['shift_description']) > 100:
            if errors:
                return_dict['errors']['Description'] = 'Description must be between 0 and 100 characters.'
            else:
                errors = True
                return_dict['status'] = "error"
                return_dict['errors'] = {'Description': 'Description must be between 0 and 100 characters.'}

    if 'shift_start_time' in form:
        try:
            datetime.datetime.strptime(form['shift_start_time'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            if errors:
                return_dict['errors']['Start Time'] = 'Incorrect Date format for start time.'
            else:
                errors = True
                return_dict['status'] = "error"
                return_dict['errors'] = {'Start Time': 'Incorrect Date format for start time.'}

    if 'shift_end_time' in form:
        try:
            datetime.datetime.strptime(form['shift_end_time'], '%Y-%m-%dT%H:%M:%S')
        except ValueError:
            if errors:
                return_dict['errors']['End Time'] = 'Incorrect Date format for end time.'
            else:
                errors = True
                return_dict['status'] = "error"
                return_dict['errors'] = {'End Time': 'Incorrect Date format for end time.'}

    return return_dict


def shift_form_errors_to_dict(form):
    """
    converts the errors from a shift form into a dict
    2007-04-05T14:30
    :param form:
    :return:
    """
    errors_dict = {
        'Description': [],
        'Create Multiple Checkbox': [],
        'Day Selector': [],
        'Start Time': [],
        'End Time': [],
        'Shift Id': []
    }
    for error in form.shift_description.errors:
        errors_dict['Description'].append(error)

    for error in form.shift_repeating.errors:
        errors_dict['Create Multiple Checkbox'].append(error)

    for error in form.shift_repeat_list.errors:
        errors_dict['Day Selector'].append(error)

    for error in form.shift_start_time.errors:
        errors_dict['Start Time'].append(error)

    for error in form.shift_end_time.errors:
        errors_dict['End Time'].append(error)

    for error in form.shift_id.errors:
        errors_dict['Shift Id'].append(error)

    return errors_dict


def validate_invite_user(form):
    email_regex = r'[^@]+@[^@]+\.[^@]+'
    return_dict = {}
    errors = False

    if 'email' not in form or len(form['email']) < 1:
        return_dict['status'] = "error"
        return_dict['errors'] = {'Invalid Email': "Field Empty"}
        errors = True
    else:
        if not re.match(email_regex, form['email']):
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Email': "Incorrect Format"}
            errors = True

    if 'first_name' not in form or len(form['first_name']) < 1:
        if errors:
            return_dict['errors']['Invalid First Name'] = "Field Empty"
        else:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid First Name': "Field Empty"}
            errors = True
    elif len(form['first_name']) > 20:
        if errors:
            return_dict['errors']['Invalid First Name'] = "Must be less than 20 characters"
        else:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid First Name': "Must be less than 20 characters"}

    if 'last_name' not in form or len(form['last_name']) < 1:
        if errors:
            return_dict['errors']['Invalid Last Name'] = "Field Empty"
        else:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Last Name': "Field Empty"}
            errors = True
    elif len(form['last_name']) > 20:
        if errors:
            return_dict['errors']['Invalid Last Name'] = "Must be less than 20 characters"
        else:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Last Name': "Must be less than 20 characters"}

    return return_dict


def validate_position(form):

    return_dict = {}

    if 'title' not in form or len(form['title']) < 1:
        return_dict['status'] = "error"
        return_dict['errors'] = {'Invalid Name': "Field Empty"}
    elif len(form['title']) > 50:
        return_dict['status'] = "error"
        return_dict['errors'] = {'Invalid Name': "Must be less than 50 characters."}

    return return_dict


def rgb_to_hex(red, green, blue):
    """Return color as #rrggbb for the given color values."""
    return '#%02x%02x%02x' % (red, green, blue)


def random_color():
    """
    Generates a random color
    :return:
    """

    red = randint(0,255)
    green = randint(0,255)
    blue = randint(0,255)

    return rgb_to_hex(red, green, blue)


def random_pastel():
    """
    Generates a random pastel color
    :return:
    """
    red_mix = 255
    green_mix = 255
    blue_mix = 255

    red = (randint(0,255) + red_mix) * .5
    green = (randint(0,255) + green_mix) * .5
    blue = (randint(0,255) + blue_mix) * .5

    return rgb_to_hex(red, green, blue)




