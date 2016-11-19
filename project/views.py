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
from project.email import ts
from decorators import check_confirmed, owns_organization, organization_member, admin_of_org, shift_belongs_to_org
import utils.organization
import utils.utils
from utils.organization import assign_member_to_position, unassign_member_to_position
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


@main_blueprint.route('/organization/<int:key>', methods=['GET', 'POST'])
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
    membership = utils.organization.get_membership(org, g.user)
    return render_template('main/organization.html',
                           organization=org,
                           form=InviteForm(),
                           form1=PositionForm(),
                           shift_form=ShiftForm(),
                           membership=membership)


@main_blueprint.route('/organization/<int:key>/shifts')
@login_required
@organization_member
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


@main_blueprint.route('/organization/<int:key>/shift/create', methods=['GET', 'POST'])
@login_required
@check_confirmed
# @owns_organization
def create_shift(key):
    """
    Creates a new shift.  Shifts can be assigned to a user or left empty at
    initialization, but are always related to a position, which is in turn
    related to an organization
    :param key:
    :return:
    """
    form = ShiftForm(request.form)
    return_dict = {}
    shift_assigned_member_id = None

    return_dict = utils.utils.validate_shift(request.form, pos_required=True)

    # print request.form['shift_position_id']
    # print type(request.form['shift_position_id'])

    if 'status' in return_dict:
        return Response(response=json.dumps(return_dict),
                        status=200,
                        mimetype="application/json")

    shift_position_id = int(request.form['shift_position_id'])
    if 'shift_assigned_member_id' in request.form:
        shift_assigned_member_id = int(request.form['shift_assigned_member_id'])

    shifts = utils.organization.create_shifts_form(shift_position_id,
                                                   shift_assigned_member_id,
                                                   request.form['shift_start_time'],
                                                   request.form['shift_end_time'],
                                                   request.form['shift_description'],
                                                   request.form['shift_repeat_list'])
    return_dict['shifts'] = shifts
    return_dict['status'] = "success"
    """

    else:
        return_dict['status'] = "error"
        errors_dict = utils.utils.shift_form_errors_to_dict(request.form)

        manual_validation = utils.utils.shift_form_errors_to_dict(form)
        if 'status' in manual_validation:
            errors_dict = utils.utils.merge_dicts(manual_validation['errors'], errors_dict)
        return_dict['errors'] = errors_dict
    """

    response = Response(response=json.dumps(return_dict),
                        status=200,
                        mimetype="application/json")

    return response


@main_blueprint.route('/organization/<int:key>/shift/<int:key1>/time', methods=['POST', ])
@login_required
@check_confirmed
@owns_organization
@shift_belongs_to_org
def update_shift_time(key, key1):
    """
    updates the shift start and end time
    :param key:
    :param key1:
    :return:
    """

    start_time = request.form['start']
    end_time = request.form['end']

    shift = Shift.query.get(key1)
    shift.update(start_time=start_time, end_time=end_time)
    response_dict = json.dumps({'status': 'success', 'shift': utils.organization.shift_to_dict(shift)})

    response = Response(response=json.dumps(response_dict),
                        status=200,
                        mimetype="application/json")

    return response


@main_blueprint.route('/organization/<int:key>/shift/<int:key1>/delete', methods=['DELETE', ])
@login_required
@check_confirmed
@owns_organization
@shift_belongs_to_org
def delete_shift(key, key1):
    """
    Deletes a shift
    :param key:
    :param key1:
    :return:
    """
    utils.organization.delete_shift(key1)

    response_dict = {
        'status': 'success',
        'message': 'Shift with id ' + str(key1) + ' successfully deleted',
    }

    response = Response(response=json.dumps(response_dict),
                        status=200,
                        mimetype="application/json")

    return response


@main_blueprint.route('/organization/<int:key>/shift/<int:key1>/update', methods=['POST'])
@login_required
@check_confirmed
@owns_organization
@shift_belongs_to_org
def update_shift(key, key1):
    """
    Updates an existing shift.
    :param key:
    :param key1:
    :return:
    """
    shift = utils.organization.get_shift(key1)
    form = ShiftForm(request.form)
    response_dict = {}
    shift_position_id = None
    shift_assigned_member_id = None

    return_dict = utils.utils.validate_shift(request.form)
    if 'status' in return_dict:
        return Response(response=json.dumps(return_dict),
                        status=200,
                        mimetype="application/json")

    if 'shift_position_id' in request.form:
        shift_position_id = int(request.form['shift_position_id'])
    if 'shift_assigned_member_id' in request.form:
        shift_assigned_member_id = int(request.form['shift_assigned_member_id'])

    shift = shift.update(position_id=shift_position_id,
                         assigned_user_id=shift_assigned_member_id,
                         start_time=request.form['shift_start_time'],
                         end_time=request.form['shift_end_time'],
                         description=request.form['shift_description'])
    response_dict['status'] = 'success'
    response_dict['message'] = 'Shift succesfully updated'
    response_dict['shift'] = utils.organization.shift_to_dict(shift)

    """
    else:
        response_dict['status'] = "error"
        errors_dict = utils.utils.shift_form_errors_to_dict(request.form)

        manual_validation = utils.utils.shift_form_errors_to_dict(form)
        if 'status' in manual_validation:
            errors_dict = utils.utils.merge_dicts(manual_validation['errors'], errors_dict)
            response_dict['errors'] = errors_dict
    """


    return Response(response=json.dumps(response_dict),
                    status=200,
                    mimetype="application/json")


@main_blueprint.route('/organization/<int:key>/invite', methods=['GET', 'POST'])
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
        return_dict = utils.organization.invite_member(org,
                                                       form.email.data,
                                                       form.first_name.data,
                                                       form.last_name.data)

    else:
        return_dict['status'] = "error"
        errors_dict = {
            'First Name': [],
            'Last Name': [],
            'Email': [],
        }

        for error in form.first_name.errors:
            errors_dict['First Name'].append(error)

        for error in form.last_name.errors:
            errors_dict['Last Name'].append(error)

        for error in form.email.errors:
            errors_dict['Email'].append(error)

        return_dict['errors'] = errors_dict

    response = Response(response=json.dumps(return_dict),
                        status=200,
                        mimetype="application/json")

    return response


@main_blueprint.route('/organization/<int:key>/join/<token>', methods=['GET', 'POST'])
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
        return redirect('/organization/' + str(key) + '/setup/' + str(token))

    else:
        utils.organization.confirm_invite(membership)
        return redirect(url_for('main.home'))


@main_blueprint.route('/organization/<int:key>/setup/<token>', methods=['GET', 'POST'])
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


@main_blueprint.route('/organization/<int:key>/create_position', methods=['POST'])
@login_required
@check_confirmed
@owns_organization
def create_position(key):

    # the new create_position function.
    org = utils.organization.get_organization(key)
    form1 = PositionForm(request.form)
    return_dict = {}

    utils.organization.create_position(org, request.form['name'])
    return_dict['status'] = "success"


    """
     if form1.validate_on_submit():
        utils.organization.create_position(org, form1.name.data)
        return_dict['status'] = "success"
    else:

        print str(form1.csrf_token.errors)

        return_dict['status'] = "error"
        errors_dict = {
            'title': []
        }

        for error in form1.name.errors:
            errors_dict['title'].append(error)

        return_dict['errors'] = errors_dict
    """


    response = Response(response=json.dumps(return_dict),
                        status=200,
                        mimetype="application/json")

    return response


@app.route('/positionsinorg/<int:key>')
def getpositioninorg(key):
    """

    :param key:
    :return:
    """
    return utils.organization.get_positions_for_org_JSON(key)


@app.route('/organization/<int:key>/position/<int:key2>/users')
def get_position_members(key, key2):
    """
    Returms a json list of all users for a position
    :param key:
    :param key2:
    :return:
    """
    print key2
    response = Response(response=utils.organization.get_members_for_position(key2),
                        status=200,  mimetype="application/json")
    return response

@app.route('/getpositionmembers/<key>/')
def get_position_users(key):
    """
    Returms a json list of all users for a position
    :param key:
    :param key2:
    :return:
    """
    response = Response(response=utils.organization.get_users_for_position(key),
                        status=200,  mimetype="application/json")
    return response


@app.route('/assign/<key>/<key1>', methods=['POST'])
@login_required
@check_confirmed
def assign(key, key1):
    """

    :return:
    """
    response = Response(response=assign_member_to_position(key, key1),
                        status=200)
    return response


@app.route('/unassign/<int:key1>/<int:key2>', methods=['POST'])
@login_required
@check_confirmed
def unassign(key, key1):
    """

    :return:
    """
    # get the user, position, and org
    response = Response(response=unassign_member_to_position(key, key1),
                        status=200)
    return response


@app.route('/deleteposition/<key>', methods=['POST'])
@login_required
@check_confirmed
def deleteposition(key):
    """

    :return:
    """
    utils.organization.deletepositions(key)
    return "success"


@app.route('/getusersinorg/<int:key>')
@login_required
@organization_member
def getusersinorg(key):
    response = Response(response=utils.organization.get_users_for_org_JSON(key),
                        status=200,
                        mimetype="application/json")

    return response


@app.route('/getassignedpositions/<int:key>/<int:key2>')
def getassignedpositions(key, key2):
    response = Response(response=utils.organization.get_assigned_positions_for_user(key, key2),
                        status=200,
                        mimetype="application/json")
    return response


@app.route('/getpositionsinorg/<int:key>')
@login_required
@organization_member
def getpositionsinorg(key):
    return utils.organization.get_positions_for_org_JSON(key)


@app.route('/organization/<key>/shifts')
@login_required
#@owns_organization
def get_shifts_for_org(key):
    """
    :param key:
    :return:
    """
    response = Response(response=utils.organization.get_all_shifts_for_org_JSON(key),
                        status=200,
                        mimetype="application/json")

    return response


@app.route('/deleteuserfromorg/<key>/<key1>',  methods=['POST'])
@login_required
def deleteuserfromorg(key, key1):
    return utils.organization.delete_user_from_org(key, key1)
    

@app.route('/getmembership/<int:key>/<int:key2>')
def get_membership(key, key2):
    response = Response(response=utils.organization.get_membership_JSON(key, key2),
                        status=200,
                        mimetype="application/json")
    return response
    

@app.route('/setadmin/<int:key>', methods=['POST'])
# @owns_organization
def set_admin_privileges(key):
    response = Response(response=utils.organization.set_membership_admin(key),
                        status=200)
    return response 
  
  