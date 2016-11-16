# project/main/views.py

#################
#### imports ####
#################

import datetime

from flask import render_template, Blueprint, request, session, g, redirect, url_for, flash, Response
from flask_login import login_required, login_user
from forms import CreateForm, InviteForm, JoinForm, PositionForm, ShiftForm
from models import User, Organization, Membership, Position, Shift
from project import app, db, bcrypt
from decorators import check_confirmed, owns_organization, organization_member, admin_of_org
import utils.organization
from utils.organization import assign_member_to_position, deletepositions, unassign_member_to_position, get_users_for_org_JSON
import json

################
#    config    #
################

main_blueprint = Blueprint('main', __name__, )


@app.before_request
def load_user():
    if 'user_id' in session:
        if session["user_id"]:
            user = User.query.filter_by(id=session["user_id"]).first()
        else:
            user = {"email": "Guest"}  # Make it better, use an anonymous User instead
    else:
        user = None

    g.user = user


################
#    routes    #
################

@main_blueprint.route('/')
def landing():
    """
    A landing page with information about skedd, as well as log in and sign up links
    :return:
    """
    return render_template('main/index.html')


@main_blueprint.route('/home', methods=['GET', ])
@login_required
@check_confirmed
def home():
    """
    Renders a user's home page
    :return:
    """
    orgs = g.user.orgs_owned.all()
    memberships = g.user.memberships.filter_by(is_owner=False).all()
    return render_template('main/home.html', organizations=orgs, memberships=memberships)


@main_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
@check_confirmed
def create():
    """
    Creates a new organization belonging to the currently signed in user
    :return:
    """
    form = CreateForm(request.form)
    if form.validate_on_submit():
        org, membership = utils.organization.create_organization(form.name.data, g.user.id)
        return redirect('/organization/' + str(org.id))

    return render_template('main/create.html', form=CreateForm())


@main_blueprint.route('/organization/<key>', methods=['GET', 'POST'])
@login_required
@check_confirmed
@organization_member
def organization(key):
    """
    The home page for an organization. displays relevant positions
    and members information.
    :param key:
    :return:
    """
    org = utils.organization.get_organization(key)
    return render_template('main/organization.html',
                           organization=org,
                           form=InviteForm(),
                           form1=PositionForm(),
                           shift_form=ShiftForm())


@main_blueprint.route('/organization/<key>/shifts')
@login_required
@owns_organization
def get_shifts_for_org(key):
    """
    Gets all shifts for an organization
    :param key:
    :return:
    """
    response = Response(response=utils.organization.get_all_shifts_for_org_JSON(key),
                        status=200,
                        mimetype="application/json")

    return response


@main_blueprint.route('/organization/<key>/shift/create', methods=['GET', 'POST'])
@login_required
@check_confirmed
#@owns_organization
def create_shift(key):
    """
    Creates a new shift.  Shifts can be assigned to a user or left empty at
    initialization, but are always related to a position, which is in turn
    related to an organization
    :param org_key:
    :param pos_key:
    :return:
    """

    org = utils.organization.get_organization(key)
    form = ShiftForm(request.form)
    return_dict = {}

    if form.validate_on_submit():

        shifts = utils.organization.create_shifts_form(request.form['shift_position_id'],
                                                       request.form['shift_assigned_member_id'],
                                                       form.shift_start_time.data,
                                                       form.shift_end_time.data,
                                                       form.shift_description.data,
                                                       form.shift_repeat_list.data)

        return_dict['shifts'] = shifts
        return_dict['status'] = "success"
    else:
        return_dict['status'] = "error"
        errors_dict = {
            'shift_description': [],
            'shift_repeating': [],
            'shift_repeat_list': [],
            'shift_start_time': [],
            'shift_end_time': [],
            'shift_id': []
        }

        for error in form.shift_description.errors:
            errors_dict['shift_description'].append(error)

        for error in form.shift_repeating.errors:
            errors_dict['shift_repeating'].append(error)

        for error in form.shift_repeat_list.errors:
            errors_dict['shift_repeat_list'].append(error)

        for error in form.shift_start_time.errors:
            errors_dict['shift_start_time'].append(error)

        for error in form.shift_end_time.errors:
            errors_dict['shift_end_time'].append(error)

        for error in form.shift_id.errors:
            errors_dict['shift_id'].append(error)

        return_dict['errors'] = errors_dict
    response = Response(response=json.dumps(return_dict),
                    status=200,
                    mimetype="application/json")

    return response


@main_blueprint.route('/organization/<key>/shift/<key1>/time', methods=['POST',])
@login_required
@check_confirmed
@owns_organization
def update_shift_time(key, key1):
    """
    updates the shift start and end time
    :param key:
    :param key1:
    :return:
    """
    shift = Shift.query.get(key1)
    shift.update_time(request.form['start'], request.form['end'])
    response_dict =  json.dumps({'status': 'success', 'shift': utils.organization.shift_to_dict(shift)})

    response = Response(response=json.dumps(response_dict),
                    status=200,
                    mimetype="application/json")

    return response


@main_blueprint.route('/organization/<org_key>/position/<pos_key>/shift/<shift_key>/edit', methods=['GET', 'POST'])
@login_required
@check_confirmed
#@owns_organization
def update_shift(org_key, pos_key, shift_key):
    """
    Updates an existing shift.
    :param org_key:
    :param pos_key:
    :param shift_key:
    :return:
    """
    shift = utils.organization.get_shift(shift_key)
    form = ShiftForm(obj=shift)
    if request.method == 'GET':
        if form.validate():
            # pre-populate form with current data
            form.populate_obj(shift)
        return render_template('main/update_shift.html', form=form)
    else:
        shift.update(pos_key, form.shift_assigned_member_id.data, form.shift_start_time.data,
                        form.shift_end_time.data, form.shift_description.data)
    return redirect(url_for('main.position', key=org_key, key2=pos_key))


@main_blueprint.route('/organization/<key>/invite', methods=['GET', 'POST'])
@login_required
@check_confirmed
@owns_organization
def invite(key):
    """
    Invites a user to the organization.  If the user does not already exist, will create
    a temporary user that can be confirmed by the invitee through an activation link
    :param key:
    :return:
    """
    org = utils.organization.get_organization(key)
    form = InviteForm(request.form)
    return_dict = {}

    if form.validate_on_submit():
        utils.organization.invite_member(org, form.email.data, form.first_name.data, form.last_name.data)
        return_dict['status'] = "success"
    else:
        return_dict['status'] = "error"
        errors_dict = {
            'first_name': [],
            'last_name': [],
            'email': [],
        }

        for error in form.first_name.errors:
            errors_dict['first_name'].append(error)

        for error in form.last_name.errors:
            errors_dict['last_name'].append(error)

        for error in form.email.errors:
            errors_dict['email'].append(error)

        return_dict['errors'] = errors_dict

    response = Response(response=json.dumps(return_dict),
                    status=200,
                    mimetype="application/json")

    return response


@main_blueprint.route('/organization/<key>/join/<token>', methods=['GET', 'POST'])
def confirm_invite(key, token):
    """

    :param key:
    :param token:
    :return:
    """

    membership = utils.organization.membership_from_key_token(key, token)
    if membership is None:
        flash('Invalid or expired confirmation link', 'danger')
        return redirect(url_for('main.home'))

    if not membership.member.confirmed:
        return redirect('/organization/' + key + '/setup/' + token)

    else:
        utils.organization.confirm_invite(membership)
        return redirect(url_for('main.home'))

@main_blueprint.route('/organization/<key>/setup/<token>', methods=['GET', 'POST'])
def setup_account(key, token):
    """

    :param key:
    :param token:
    :return:
    """
    form = JoinForm()

    membership = utils.organization.membership_from_key_token(key, token)
    if membership is None:
        flash('Invalid or expired confirmation link', 'danger')
        return redirect(url_for('main.home'))

    if form.validate_on_submit():
        utils.organization.confirm_user(membership.member, form.password.data)
        utils.organization.confirm_invite(membership)
        return redirect(url_for('main.home'))
    else:
        return render_template('main/setup.html', form=form, organization=membership.organization)


@main_blueprint.route('/organization/<key>/create_position', methods=['GET', 'POST'])
@login_required
@check_confirmed
@owns_organization
def create_position(key):

    #the new create_position function.
    org = utils.organization.get_organization(key)
    form1 = PositionForm(request.form)
    return_dict = {}

    if form1.validate_on_submit():
        utils.organization.create_position(org, form1.name.data)
        return_dict['status'] = "success"
    else:
        return_dict['status'] = "error"
        errors_dict = {
            'title': []
        }

        for error in form1.name.errors:
            errors_dict['title'].append(error)

        return_dict['errors'] = errors_dict

    response = Response(response=json.dumps(return_dict),
                    status=200,
                    mimetype="application/json")

    return response

@app.route('/positionsinorg/<key>')
def getpositioninorg(key):
    """

    :param key:
    :return:
    """
    return utils.organization.get_positions_for_org_JSON(key)


@app.route('/organization/<key>/position/<key2>/users')
def get_position_members(key, key2):
    """
    Returms a json list of all users for a position
    :param key:
    :param key2:
    :return:
    """
    response = Response(response=utils.organization.get_members_for_position(key2),
                        status=200,  mimetype="application/json")
    return response


@app.route('/assign/<key1>/<key2>', methods=['POST'])
@login_required
@check_confirmed
def assign(key1, key2):
    """

    :return:
    """
    response = Response(response=assign_member_to_position(key1, key2),
                        status=200)
    return response


@app.route('/unassign/<key1>/<key2>', methods=['POST'])
@login_required
@check_confirmed
def unassign(key1, key2):
    """

    :return:
    """
    # get the user, position, and org
    response = Response(response=unassign_member_to_position(key1, key2),
                        status=200)
    return response


@app.route('/getusersinorg/<key>')
@login_required
@owns_organization
def getusersinorg(key):
    response = Response(response=utils.organization.get_users_for_org_JSON(key),
                        status=200,
                        mimetype="application/json")

    return response

@app.route('/getassignedpositions/<key>/<key2>')
def getassignedpositions(key, key2):
    response = Response(response=utils.organization.get_assigned_positions_for_user(key, key2),
                        status=200,
                        mimetype="application/json")
    return response

@app.route('/getpositionsinorg/<key>')
@login_required
@owns_organization
def getpositionsinorg(key):
    return utils.organization.get_positions_for_org_JSON(key)
    
@app.route('/getmembership/<key>/<key2>')
def get_membership(key, key2):
    response = Response(response=utils.organization.get_membership_JSON(key, key2),
                        status=200,
                        mimetype="application/json")
    return response
    
@app.route('/setadmin/<key>', methods=['POST'])
# @owns_organization write new one to work with membership_id?
def set_admin_privileges(key):
    response = Response(response=utils.organization.set_membership_admin(key),
                        status=200)
    return response
