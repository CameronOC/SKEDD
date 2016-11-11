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
from decorators import check_confirmed, owns_organization
from project.email import send_email
import utils.organization
from utils.organization import assign_member_to_position, deletepositions, unassign_member_to_position, get_users_for_org_JSON
from utils.token import confirm_token, generate_invitation_token
from flask_security import current_user
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


@main_blueprint.route('/organization/<key>', methods=['GET', ])
@login_required
@check_confirmed
def organization(key):
    """
    The home page for an organization. displays relevant positions
    and members information.
    :param key:
    :return:
    """
    org = utils.organization.get_organization(key)
    return render_template('main/organization.html', organization=org)


@main_blueprint.route('/organizationc/<key>', methods=['GET', ])
@login_required
@check_confirmed
def organization_calendar(key):
    """
    The home page for an organization. displays relevant positions
    and members information.
    :param key:
    :return:
    """
    org = utils.organization.get_organization(key)
    return render_template('main/organizationc.html', organization=org, form=InviteForm())


@main_blueprint.route('/organization/<org_key>/position/<pos_key>/shift/create', methods=['GET', 'POST'])
@login_required
@check_confirmed
#@owns_organization
def create_shift(org_key, pos_key):
    """
    Creates a new shift.  Shifts can be assigned to a user or left empty at
    initialization, but are always related to a position, which is in turn
    related to an organization
    :param org_key:
    :param pos_key:
    :return:
    """
    form = ShiftForm(request.form)
    if request.method == 'GET':
        # fill in SelectField for choosing a user to assign a shift to (when creating the shift)
        form.assigned_user_id.choices = utils.organization.gather_members_for_shift(org_key)
        return render_template('main/create_shift.html', form=form)
    else:
        shift = utils.organization.create_shift(pos_key, form.assigned_user_id.data, form.day.data,
                                                form.start_time.data, form.end_time.data)
    return redirect(url_for('main.position', key=org_key, key2=pos_key))


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
        # fill in SelectField for choosing a user to assign a shift to (when creating the shift)
        form.assigned_user_id.choices = utils.organization.gather_members_for_shift(org_key)
        if form.validate():
            # pre-populate form with current data
            form.populate_obj(shift)
        return render_template('main/update_shift.html', form=form)
    else:
        utils.organization.update_shift(shift, pos_key, form.assigned_user_id.data, form.day.data,
                                        form.start_time.data, form.end_time.data)
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


@main_blueprint.route('/organization/<key>/position/<key2>', methods={'GET', 'POST'})
@login_required
@check_confirmed
def position(key, key2):
    """

    :param key:
    :return:
    """
    org = utils.organization.get_organization(key)

    pos = Position.query.filter_by(id=key2).first()
    shifts = pos.assigned_shifts.all()
    return render_template('main/position.html', position=pos, organization=org, shifts=shifts)


@main_blueprint.route('/organization/<key>/create_position', methods=['GET', 'POST'])
@login_required
@check_confirmed
@owns_organization
def create_position(key):
    """

    :param key:
    :return:
    """
    if request.method == 'GET':
        org = Organization.query.filter_by(id=key).first()
        return render_template('main/create_position.html', form=CreateForm())

    else:
        org = Organization.query.filter_by(id=key).first()
        form = PositionForm(request.form)
        if form.validate_on_submit():
            title = form.name.data
            pos = Position(title=title, organization_id=org.id)
            db.session.add(pos)
            org.owned_positions.append(pos)
            db.session.commit()

            return redirect('/organization/' + str(org.id) + '/position/' + str(pos.id))
        else:
            return redirect('/organization/' + str(org.id))

@app.route('/positionsinorg/<key>')
def getpositioninorg(key):
    """

    :param key:
    :return:
    """
    return utils.organization.get_positions_for_org_JSON(key)

@main_blueprint.route('/organization/<key>/member/<key2>', methods=['GET', ])
@login_required
@check_confirmed
@owns_organization
def manager_members_profile(key, key2):
    """

    :param key:
    :param key2:
    :return:
    """
    org = utils.organization.get_organization(key)

    user = User.query.filter_by(id=key2).first()

    return render_template('main/member.html', user=user, organization=org)


@app.route('/assign', methods=['POST'])
@login_required
@check_confirmed
def assign():
    """

    :return:
    """
    myuser = User.query.filter_by(id=request.form["assignuserid"]).first_or_404()
    mypos = Position.query.filter_by(title=request.form['position']).first_or_404()
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()
    if myuser in mypos.assigned_users:
        flash('This persons position is already assigned to ' + mypos.title, 'danger')
        return render_template('main/member.html', user=myuser, organization=org)

    assign_member_to_position(myuser, mypos, org)

    # redirects to the page before
    return redirect(url_for('main.manager_members_profile', key=org.id, key2=myuser.id))


@app.route('/assignpos', methods=['POST'])
@login_required
@check_confirmed
def assignpos():
    """

    :return:
    """
    # get the user, position, and org
    myuser = User.query.filter_by(id=request.form["userid"]).first_or_404()
    mypos = Position.query.filter_by(id=request.form['positionid']).first_or_404()
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()
    # if this user already exists return flash
    if myuser in mypos.assigned_users:
        flash('This persons position is already assigned to ' + mypos.title, 'danger')
        return render_template('main/position.html', position=mypos, organization=org)

    assign_member_to_position(myuser, mypos, org)
    
    # redirects to the page before
    return render_template('main/position.html', position=mypos, organization=org)


@app.route('/unassign', methods=['POST'])
@login_required
@check_confirmed
def unassign():
    """

    :return:
    """
    # get the user, position, and org
    myuser = User.query.filter_by(id=request.form["unassignuserid"]).first_or_404()
    mypos = Position.query.filter_by(id=request.form["unassignposid"]).first_or_404()
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()
    
    unassign_member_to_position(myuser, mypos, org)
    # redirects to the page before
    return redirect(url_for('main.manager_members_profile', key=org.id, key2=myuser.id))


@app.route('/unassignpos', methods=['POST'])
@login_required
@check_confirmed
def unassignpos():
    """

    :return:
    """
    # get the user, position, and org
    myuser = User.query.filter_by(id=request.form["unassignuserid"]).first_or_404()
    mypos = Position.query.filter_by(id=request.form["unassignposid"]).first_or_404()
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()

    unassign_member_to_position(myuser, mypos, org)
    
    # redirects to the page before
    return render_template('main/position.html', position=mypos, organization=org)


@app.route('/deleteposition', methods=['POST'])
@login_required
@check_confirmed
def deleteposition():
    """

    :return:
    """
    pos = Position.query.filter_by(id=request.form["deleteposid"]).first_or_404()
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()

    deletepositions(pos, org)

    return render_template('main/organization.html', organization=org)

@app.route('/getusersinorg/<key>')
def getusersinorg(key):
    return utils.organization.get_users_for_org_JSON(key)

@app.route('/getpositionsinorg/<key>')
def getpositionsinorg(key):
    return utils.organization.get_positions_for_org_JSON(key)