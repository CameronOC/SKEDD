from datetime import datetime, timedelta
import json
from project import db, bcrypt
from project.models import Organization, User, Membership, Position, Shift
from project.email import send_email
from project.utils.token import confirm_token, generate_invitation_token

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
        joined=True
    )
    db.session.add(membership)
    db.session.commit()

    return org, membership


def get_user(id):
    """
    Gets a user by ID
    :param id:
    :return:
    """
    return User.query.get(id)


def get_organization(id):
    """
    gets an organization by id and returns the object or None
    if it doesn't exist
    :param id:
    :return:
    """
    return Organization.query.get(id)


def get_position(id):
    """
    Gets a position object based on id
    :param id:
    :return:
    """
    return Position.query.get(id)


def get_shift(id):
    """
    Gets a shift object based on id
    :param id:
    :return:
    """
    return Shift.query.get(id)


def get_membership(org, user):
    """
    Checks if a user is in an organization
    :param organization_id:
    :param user_id:
    :return:
    """
    return Membership.query.filter_by(member_id=user.id, organization_id=org.id).first()


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


def invite_member(org, email, first_name, last_name):
    """
    Invite a user to the organization id, creating a dummy account if needed
    :param organization_id:
    :return:
    """
    user = User.query.filter_by(email=email).first()

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
        flash('This person is already a member of ' + org.name, 'danger')
    else:
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

        flash('You succesfully invited ' + user.first_name + ' ' + user.last_name + '.', 'success')

    return membership


def confirm_invite(membership):
    """
    Confirms an invitation to an organization, if valid
    :param key:
    :param token:
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
    :return:
    """
    # create shift with parameters
    shift = Shift(position_id=pos_key, assigned_user_id=assigned_user_id, start_time=start_time,
                    end_time=end_time, description=description)

    # add shift to database
    db.session.add(shift)
    db.session.commit()
    return shift


def gather_members_for_shift(org_key):
    """
    Creates a formatted list of users in an organization
    to use in ShiftForm.user
    :param org_key:
    :return:
    """
    # filter users by members of current org in current position
    eligible_members = Membership.query.filter_by(organization_id=org_key).all()
    # create list to fill in SelectField
    users = []
    users.append((None, '--'))
    for c in eligible_members:
        # use 'member' backref in user-membership relationship
        users.append((c.member.id, c.member.first_name + ' ' + c.member.last_name))

    return users


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
    
    
def create_shifts_form( position_id, assigned_user_id, start_time, 
                        end_time, description, repeat_list=None):
    """
    creates a month's worth of shifts
    based on data from a form
    :param dictionary:
    :return:
    """
    shifts = []
    main_start_time = datetime.strptime(start_time, '%Y-%m-%dT%H:%M:%S')
    main_end_time = datetime.strptime(end_time, '%Y-%m-%dT%H:%M:%S')

    delta = timedelta()
    shifts.append(create_shift_helper(
                position_id,
                assigned_user_id,
                description,
                main_start_time,
                main_end_time,
                delta))

    if repeat_list is not None and len(repeat_list) > 0:
        main_day_int = main_start_time.weekday()
        for day_int in repeat_list:

            if main_day_int == day_int:
                week_ct = 1;
            else:
                week_ct = 0

            while week_ct < 4:
                day_difference = day_int - main_day_int
                delta = timedelta(days=day_difference, weeks=week_ct)
                shifts.append(create_shift_helper(
                    position_id,
                    assigned_user_id,
                    description,
                    main_start_time,
                    main_end_time,
                    delta
                ))
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
    # db.session.add(new_shift)
    # db.session.commit()
    return new_shift

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
                assigned_user_name = ''
                
            shifts_list.append({'position_id': s.position_id,
                                'assigned_user_name': assigned_user_name,
                                'assigned_user_id': s.assigned_user_id,
                                'start_time': s.start_time,
                                'end_time': s.end_time,
                                'description': s.description,
                                'id': s.id
                                })

    return json.dumps(shifts_list)
            
def get_users_for_org_JSON(org_id):
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

def get_positions_for_org_JSON(org_id):
    """
    returns all positions in an organization as a JSON
    dictionary of type str. Then converts into list of
    dictionaries using json.loads equivalent.
    :param id:
    :return:
    """
    outer = {}
    pos = Position.query.filter_by(organization_id=org_id).all()
    for p in pos:
        inner = {   'title': p.title,
                    'organization_id': p.organization_id}
        outer[str(p.id)] = inner

    return json.dumps(outer)

#used in views.deletepositions
def deletepositions(posid, orgid):
    pos = posid
    org = orgid
    #remove the position from the org
    db.session.delete(pos)
    db.session.commit()


#used in views.assign and views.assignpos
def assign_member_to_position(userid, posid, orgid):
    user = userid
    pos = posid
    org = orgid
    #assign the user to an org
    pos.assigned_users.append(user)
    db.session.commit()


def unassign_member_to_position(userid, posid, orgid):
    user = userid
    pos = posid
    org = orgid
    #removes the user from the position
    pos.assigned_users.remove(user)
    db.session.commit()
