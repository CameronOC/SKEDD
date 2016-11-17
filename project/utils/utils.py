def merge_dicts(*dict_args):
    """
    Given any number of dicts, shallow copy and merge into a new dict,
    precedence goes to key value pairs in latter dicts.
    """
    result = {}
    for dictionary in dict_args:
        result.update(dictionary)
    return result

def validate_member_position_id(form, pos_required=False):
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
            return_dict['errors'] = {'Invalid Position id: ': form['shift_position_id']}
            errors = True
        elif int(form['shift_position_id']) == 0:
            return_dict['status'] = "error"
            return_dict['errors'] = {'Invalid Position id: ': form['shift_position_id']}
            errors = True
    elif pos_required:
        return_dict['status'] = "error"
        return_dict['errors'] = {'Invalid Position id: ': 'No Position id selected'}
        errors = True

    if 'shift_assigned_member_id' in form:
        if not form['shift_assigned_member_id'].isdigit():
            if errors:

                return_dict['errors']['Invalid Member id: '] = form['shift_assigned_member_id']
            else:
                return_dict['status'] = "error"
                return_dict['errors'] = {'Invalid Member id: ': form['shift_assigned_member_id']}

    return return_dict

def shift_form_errors_to_dict(form):
    """
    converts the errors from a shift form into a dict
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

def membership_to_dict(membership):
    """
    Converts a membership object to a dictionary
    :param membership:
    :return:
    """
    if membership is None or not isinstance(membership, Membership):
        return None

    membership_dict = {
        'id': membership.id,
        'member_id': membership.member_id,
        'organization_id': membership.organization_id,
        'is_owner': membership.is_owner,
        'is_admin': membership.is_admin,
        'joined': membership.joined,
    }

    return membership_dict