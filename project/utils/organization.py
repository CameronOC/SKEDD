from datetime import datetime, timedelta
import json
from project import db, bcrypt
from project.email import send_email, ts
from project.models import Organization, User, Membership, Position, Shift, position_assignments
from project.utils.token import confirm_token, generate_invitation_token
import project.utils.utils as utils

from flask import render_template, flash, url_for, g
from flask_login import login_user


def create_organization(name, owner_id):
    """
    Creates a new organization with paramaters and returns the created
    organization object
    :param owner_id:
    :param name:
    :return:
    """
    org = Organization(name=name, owner_id=owner_id)
    db.session.add(org)
    db.session.commit()

    membership = Membership(
        member_id=owner_id,
        organization_id=org.id,
        is_owner=True,
        is_admin=True,
        joined=True
    )
    db.session.add(membership)
    db.session.commit()

    return org, membership


def get_user(user_id):
    """
    Gets a user by ID
    :param user_id:
    :return:
    """
    return User.query.get(user_id)


def get_organization(org_id):
    """
    gets an organization by id and returns the object or None
    if it doesn't exist
    :param org_id:
    :return:
    """
    return Organization.query.get(org_id)


def get_position(pos_id):
    """
    Gets a position object based on id
    :param pos_id:
    :return:
    """
    return Position.query.get(pos_id)


def get_shift(shift_id):
    """
    Gets a shift object based on id
    :param shift_id:
    :return:
    """
    return Shift.query.get(shift_id)


def get_membership(org, user):
    """
    Checks if a user is in an organization
    :param org:
    :param user:
    :return:
    """
    return Membership.query.filter_by(member_id=user.id, organization_id=org.id).first()


def get_membership_JSON(org, user):
    """
    Checks if a user is in an organization
    :param org:
    :param user:
    :return:
    """
    membership = Membership.query.filter_by(member_id=user, organization_id=org).first()
    membership_dict = {'id': membership.id, 'joined': membership.joined, 'is_owner': membership.is_owner,
                       'is_admin': membership.is_admin, 'member_id': membership.member_id,
                       'organization_id': membership.organization_id}
                            
    return json.dumps(membership_dict)


def confirm_user(user, password=None):
    if password is not None:
        user.password = bcrypt.generate_password_hash(password)
    user.confirmed = True
    user.confirmed_on = datetime.now()
    db.session.commit()


def membership_from_key_token(key, token):
    """
    Gets a membership with a key and a token, or returns none
    :param key:
    :param token:
    :return:
    """
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first()

    if user is None:
        return None

    org = get_organization(key)

    if org is None:
        return None

    membership = user.memberships.filter_by(organization_id=org.id).first()
    return membership


def create_position(org, title, description):
    """
    Creates a position given a organization and a position title/name
    :return:
    """
    position = Position(title=title, organization_id=org.id, description=description)
    db.session.add(position)
    org.owned_positions.append(position)
    db.session.commit()
    return position


def invite_member(org, email, first_name, last_name):
    """
    Invite a user to the organization id, creating a dummy account if needed
    :param org:
    :param email:
    :param first_name:
    :param last_name:
    :return:
    """
    user = User.query.filter_by(email=email).first()
    return_dict = {}

    if user is None:
        user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password="temp",
            confirmed=False
        )
        db.session.add(user)

    db.session.commit()

    membership = get_membership(org, user)

    if membership is not None:
        return_dict['status'] = 'error'
        return_dict['message'] = user.first_name + ' ' + user.last_name + ' is already a member of ' + org.name
        return return_dict

    membership = Membership(
        member_id=user.id,
        organization_id=org.id
    )
    db.session.add(membership)
    db.session.commit()

    token = generate_invitation_token(user.email)

    confirm_url = url_for('main.confirm_invite', key=org.id, token=token, _external=True)

    html = render_template('emails/invitation.html', confirm_url=confirm_url, user=user, organization=org)

    subject = "You've been invited to use SKEDD"

    send_email(user.email, subject, html)

    return_dict['status'] = 'success'
    return_dict['message'] = 'You succesfully invited ' + str(user.first_name) + ' ' + str(user.last_name) + '.'
    return_dict['membership'] = membership_to_dict(membership)
    return return_dict


def confirm_invite(membership):
    """
    Confirms an invitation to an organization, if valid
    :param membership:
    :return:
    """
    membership.joined = True
    db.session.commit()
    if g.user is None or g.user.id != membership.member.id:
        login_user(membership.member)
    flash('You have now joined ' + membership.organization.name, 'success')
    return membership


def create_shift(pos_key, assigned_user_id, start_time, end_time, description):
    """
    Creates a new shift object
    :param pos_key:
    :param assigned_user_id:
    :param start_time:
    :param end_time:
    :param description:
    :return:
    """
    # create shift with parameters
    print type(assigned_user_id)
    shift = Shift(position_id=pos_key, assigned_user_id=assigned_user_id, start_time=start_time,
                  end_time=end_time, description=description)

    # add shift to database
    db.session.add(shift)
    db.session.commit()
    return shift


def create_shifts_JSON(dictionary):
    """
    creates a month's worth of shifts
    based on a dictionary (JSON) argument
    :param dictionary:
    :return:
    """
    shifts = []
    main_start_time = datetime.strptime(dictionary['start_time'], '%Y-%m-%dT%H:%M:%S')
    main_end_time = datetime.strptime(dictionary['end_time'], '%Y-%m-%dT%H:%M:%S')

    delta = timedelta()
    shifts.append(create_shift_helper(
                dictionary['position_id'],
                dictionary['assigned_user_id'],
                dictionary['description'],
                main_start_time,
                main_end_time,
                delta))

    if 'repeating' in dictionary and dictionary['repeating'] is not None and len(dictionary['repeating']) > 0:
        main_day_int = main_start_time.weekday()
        for day_int in dictionary['repeating']:

            if main_day_int == day_int:
                week_ct = 1
            else:
                week_ct = 0

            while week_ct < 4:
                day_difference = day_int - main_day_int
                delta = timedelta(days=day_difference, weeks=week_ct)
                shifts.append(create_shift_helper(
                    dictionary['position_id'],
                    dictionary['assigned_user_id'],
                    dictionary['description'],
                    main_start_time,
                    main_end_time,
                    delta
                ))
                week_ct += 1

    return shifts


# noinspection PyTypeChecker
def create_shifts_form(position_id, assigned_user_id, start_time,
                       end_time, description, repeat_list=None):
    """
    creates a month's worth of shifts
    based on data from a form
    :param position_id:
    :param assigned_user_id:
    :param start_time:
    :param end_time:
    :param description:
    :param repeat_list:
    :return:
    """
    shifts = []
    main_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
    main_end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')

    delta = timedelta()

    new_shift = create_shift_helper(
                position_id,
                assigned_user_id,
                description,
                main_start_time,
                main_end_time,
                delta)

    shifts.append(shift_to_dict(new_shift))

    if repeat_list is not None and len(repeat_list) > 0:
        main_day_int = main_start_time.weekday()
        for day_int in repeat_list:

            if main_day_int == int(day_int):
                week_ct = 1
            else:
                week_ct = 0

            while week_ct < 4:
                day_difference = int(day_int) - main_day_int
                if week_ct == 0:
                    if day_int > main_day_int:
                        delta = timedelta(days=day_difference, weeks=0)
                        new_shift = create_shift_helper(
                            position_id,
                            assigned_user_id,
                            description,
                            main_start_time,
                            main_end_time,
                            delta)

                        shifts.append(shift_to_dict(new_shift))

                else:
                    delta = timedelta(days=day_difference, weeks=week_ct)
                    new_shift = create_shift_helper(
                            position_id,
                            assigned_user_id,
                            description,
                            main_start_time,
                            main_end_time,
                            delta)

                    shifts.append(shift_to_dict(new_shift))

                week_ct += 1

    return shifts


def create_shift_helper(position_id, assigned_user_id, description, start_time, end_time, delta):
    """
    creates a shift and returns the object base on parameters
    :param position_id:
    :param assigned_user_id:
    :param description:
    :param start_time:
    :param end_time:
    :param delta:
    :return:
    """
    new_start_time = (start_time + delta).strftime('%Y-%m-%dT%H:%M:%S')
    new_end_time = (end_time + delta).strftime('%Y-%m-%dT%H:%M:%S')
    new_shift = create_shift(position_id,
                             assigned_user_id,
                             new_start_time,
                             new_end_time,
                             description
                             )
    db.session.add(new_shift)
    db.session.commit()
    return new_shift


def delete_shift(shift_id):
    """
    deletes a shift
    :param shift_id:
    :return:
    """
    shift = Shift.query.get(shift_id)
    db.session.delete(shift)
    db.session.commit()


def membership_to_dict(membership):
    """
    Converts a membership object to a dictionary
    :param membership:
    :return:
    """
    if membership is None:
        return None

    if not isinstance(membership, Membership):
        raise TypeError(str(type(membership)) + ' is not type Membership')

    membership_dict = {
        'id': membership.id,
        'member_id': membership.member_id,
        'organization_id': membership.organization_id,
        'is_owner': membership.is_owner,
        'is_admin': membership.is_admin,
        'joined': membership.joined,
    }

    return membership_dict

def shift_to_dict(shift):
    """
    Takes a shift object and returns a dictionary representation
    :param shift:
    :return:
    """

    if shift is None:
        return None

    if not isinstance(shift, Shift):
        raise TypeError(str(type(shift)) + ' is not type Shift')

    shift_dict = {
        'id': shift.id,
        'position_id': shift.position_id,
        'position_title': shift.Position.title,
        'start': shift.start_time,
        'end': shift.end_time,
    }

    if shift.description is None:
        shift_dict['description'] = ''
    else:
        shift_dict['description'] = shift.description

    if shift.user is not None:
        shift_dict['assigned_member_id'] = shift.assigned_user_id
        shift_dict['assigned_member'] = shift.user.first_name + ' ' + shift.user.last_name

    else:
        shift_dict['assigned_member_id'] = 0
        shift_dict['assigned_member'] = 'Unassigned'

    return shift_dict


def get_all_shifts_for_org_JSON(org_id):
    """
    returns all shifts for each position
    in an organization as a JSON dictionary
    of type str. Convert into dictionary of
    dictionaries using json.loads equivalent.
    :param org_id:
    :return:
    """
    shifts_list = []
    positions = Position.query.filter_by(organization_id=org_id).all()
    for p in positions:
        shifts = Shift.query.filter_by(position_id=p.id).all()
        for s in shifts:
        
            if s.user is not None:
                assigned_user_name = s.user.first_name + ' ' + s.user.last_name
            else:
                assigned_user_name = 'Unassigned'
                
            shifts_list.append({'position_id': s.position_id,
                                'title': s.Position.title,
                                'assigned_member': assigned_user_name,
                                'assigned_member_id': s.assigned_user_id,
                                'start': s.start_time,
                                'end': s.end_time,
                                'description': s.description,
                                'id': s.id,
                                'color': p.color
                                })

    return json.dumps(shifts_list)


def get_users_for_org_JSON(org_id):
    """

    :param org_id:
    :return:
    """
    members_list = []
    members = Membership.query.filter_by(organization_id=org_id).all()
    for member in members:
        members_list.append({
            'first_name': member.member.first_name,
            'last_name': member.member.last_name,
            'email': member.member.email,
            'id': member.member.id
        })

    return json.dumps(members_list)


def get_users_for_position(position_id):
    """
    returns a JSON list of users that are assigned to a position
    :param position_id:
    :return:
    """
    members_list = []

    position = Position.query.get(position_id)
    members = position.assigned_users

    for member in members:
        members_list.append({
            'first_name': member.first_name,
            'last_name': member.last_name,
            'id': member.id
        })

    #return json.dumps({
    #    'status': 'success',
    #    'members': members_list
    #})
    return json.dumps(members_list)


def get_members_for_position(position_id):
    """
    returns a JSON list of users that are assigned to a position
    :param position_id:
    :return:
    """
    members_list = []
    if position_id != 0:
        position = Position.query.get(position_id)
        members = position.assigned_users

        for member in members:
            members_list.append({
                'first_name': member.first_name,
                'last_name': member.last_name,
                'id': member.id
            })

    return json.dumps({
        'status': 'success',
        'members': members_list
    })


def get_positions_for_org_JSON(org_id):
    """
    returns all positions in an organization as a JSON
    dictionary of type str. Then converts into list of
    dictionaries using json.loads equivalent.
    :param org_id:
    :return:
    """
    positions_list = []
    pos = Position.query.filter_by(organization_id=org_id).all()
    for p in pos:
        positions_list.append({   
                    'title': p.title,
                    'organization_id': p.organization_id,
                    'id': p.id,
                    'description': p.description
        })

    return json.dumps(positions_list)


#used in views.deletepositions
def deletepositions(posid):
    """

    :param posid:
    :return:
    """
    position = Position.query.filter_by(id=posid).first()
    shifts = Shift.query.filter_by(position_id=posid).all()
    if shifts is not None:
      for shift in shifts:
          db.session.delete(shift)
    #remove the position from the org
    db.session.delete(position)
    db.session.commit()


# used in views.assign and views.assignpos
def assign_member_to_position(user, pos):
    """
    assign the user to an org
    :param user:
    :param pos:
    :return:
    """
    myuser = User.query.filter_by(id=user).first()
    mypos = Position.query.filter_by(id=pos).first()
    #mypos.assigned_users.append(myuser)
    if db.session.query(position_assignments).filter(position_assignments.c.user_id==user, position_assignments.c.position_id==pos).first() == None:
    #if position_assignments.query.filter_by(user_id=user, position_id=pos) == None:
        mypos.assigned_users.append(myuser)
        db.session.commit()
        return "success"
    else:
        #flash('member already assigned to this position', category='error')
        return "already assigned"


def unassign_member_to_position(user, pos):
    """

    :param user:
    :param pos:
    :return:
    """
    myuser = User.query.filter_by(id=user).first()
    mypos = Position.query.filter_by(id=pos).first()

    # removes the user from the position
    mypos.assigned_users.remove(myuser)
    db.session.commit()
    return "success"

def get_assigned_positions_for_user(orgid, userid):
    """

    :param orgid:
    :param userid:
    :return:
    """
    assigned_list = []
    org = Organization.query.filter_by(id=orgid).first()
    for pos in org.owned_positions:
        for person in pos.assigned_users:
            if str(person.id) == str(userid):
                assigned_list.append({ 
                    'title': pos.title,
                    'position_id': pos.id,
                    'user_id': person.id
                 })

    return json.dumps(assigned_list)



def delete_user_from_org(userid, orgid):
    """

    :param userid:
    :param orgid:
    :return:
    """
    user = User.query.filter_by(id=userid).first()
    org = Organization.query.filter_by(id=orgid).first()
    membership = get_membership(org, user)
    #db.session.delete(membership)
    #db.session.commit()

    poss = Position.query.filter_by(organization_id=orgid).all()
    print poss
    for position in poss:
        if db.session.query(position_assignments).filter(position_assignments.c.user_id==userid, position_assignments.c.position_id==position.id).first() != None:
            position.assigned_users.remove(user)
            db.session.commit()

    #Because shifts doesn't have a orgid col
    #go through all the positions in the org
    #for each position find all shifts
    #if that shift has the same userid as the user
    #set it to none.
    positions = Position.query.filter_by(organization_id=orgid).all()
    for position in positions:
        shifts = Shift.query.filter_by(position_id=position.id).all()
        for shift in shifts:
            if shift.assigned_user_id == userid:
                shift.assigned_user_id = None
    db.session.commit()

    #find all position assignments for that user in that org and delete them
    #someone should fix this

    db.session.delete(membership)
    db.session.commit()

    return "success"

    
def set_membership_admin(mem_id):
    """

    :param mem_id:
    :return:
    """
    membership = Membership.query.filter_by(id=mem_id).first()
    membership.change_admin()
    return "success"
    
    
def send_password_recovery_email(email):
    """

    :param email:
    :return:
    """
    user = User.query.filter_by(email=email).first()
    
    token = ts.dumps(user.email, salt='recover-key')

    reset_url = url_for('user.recover_password', token=token, _external=True)

    html = render_template('emails/password_reset_request.html', reset_url=reset_url, user=user)

    subject = "SKEDD - Password Reset Requested"

    send_email(user.email, subject, html)

    flash('Password reset email sent to ' + email, 'success')    

