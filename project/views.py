# project/main/views.py

#################
#### imports ####
#################

import datetime

from flask import render_template, Blueprint, request, session, g, redirect, url_for, flash
from flask_login import login_required, login_user
from forms import CreateForm, InviteForm, JoinForm, PositionForm, ShiftForm
from models import User, Organization, Membership, Position, Shift
from project import app, db, bcrypt
from decorators import check_confirmed, owns_organization
from project.email import send_email
import utils.organization
from utils.token import confirm_token, generate_invitation_token

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
    return render_template('main/index.html')


@main_blueprint.route('/home', methods=['GET', ])
@login_required
@check_confirmed
def home():
    orgs = g.user.orgs_owned.all()
    memberships = g.user.memberships.filter_by(is_owner=False).all()
    return render_template('main/home.html', organizations=orgs, memberships=memberships)


@main_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = CreateForm(request.form)
    if form.validate_on_submit():
        org, membership = utils.organization.create_organization(form.name.data, g.user.id)
        return redirect('/organization/' + str(org.id))

    return render_template('main/create.html', form=CreateForm())


@main_blueprint.route('/organization/<key>', methods=['GET', ])
@login_required
def organization(key):
    org = utils.organization.get_organization(key)
    return render_template('main/organization.html', organization=org)


@main_blueprint.route('/organization/<key1>/member/<key2>', methods=['GET', ])
@login_required
@owns_organization
# add owns_org
def manager_members_profile(key1, key2):
    org = utils.organization.get_organization(key)

    user = User.query.filter_by(id=key2).first()

    return render_template('main/member.html', user=user, organization=org)


@main_blueprint.route('/organization/<orgKey>/position/<posKey>/shift/create', methods=['GET', 'POST'])
@login_required
def shift(org_key, pos_key):
    if request.method == 'GET':
        form = ShiftForm()
        memberships = Membership.query.filter_by(organization_id=org_key).all()
        for c in memberships:
            form.user.choices.append((c.member.id, c.member.first_name + ' ' + c.member.last_name))
        return render_template('main/create_shift.html', form=form)
    else:
        assigned_user_id = request.form['user']
        day = request.form['day']
        start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M')
        end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M')

        shift = Shift(position_id=pos_key, assigned_user_id=assigned_user_id, day=day, start_time=start_time,
                      end_time=end_time)

        db.session.add(shift)
        db.session.commit()

        return redirect(url_for('main.position', key=org_key, key2=pos_key))


@main_blueprint.route('/organization/<key>/invite', methods=['GET', 'POST'])
@login_required
def invite(key):
    org = utils.organization.get_organization(key)
    form = InviteForm(request.form)
    if form.validate_on_submit():
        utils.organization.invite_member(org, form.email.data, form.first_name.data, form.last_name.data)

    return render_template('main/invite.html', form=InviteForm(), organization=org)


@main_blueprint.route('/organization/<key>/join/<token>', methods=['GET', 'POST'])
def confirm_invite(key, token):
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    org = utils.organization.get_organization(key)
    membership = user.memberships.filter_by(organization_id=org.id).first_or_404()

    if not user.confirmed:
        return redirect('/organization/' + key + '/setup/' + token)
    else:
        membership.joined = True
        db.session.commit()
        if g.user is None or g.user.id != user.id:
            login_user(user)
        flash('You have now joined ' + org.name, 'success')
        return redirect(url_for('main.home'))

@main_blueprint.route('/organization/<key>/setup/<token>', methods=['GET', 'POST'])
def setup_account(key, token):
    form = JoinForm()
    email = confirm_token(token)
    user = User.query.filter_by(email=email).first_or_404()
    org = utils.organization.get_organization(key)
    membership = user.memberships.filter_by(organization_id=org.id).first_or_404()
    if form.validate_on_submit():
        # will need error handling
        user.password = bcrypt.generate_password_hash(form.password.data)
        user.confirmed = True
        user.confirmed_on = datetime.datetime.now()
        membership.joined = True
        db.session.commit()
        if g.user is None or g.user.id != user.id:
            login_user(user)
        flash('You have now joined ' + org.name, 'success')
        return redirect(url_for('main.home'))
    else:
        return render_template('main/setup.html', form=form, organization=org)


@main_blueprint.route('/organization/<key>/position/<key2>', methods={'GET', 'POST'})
@login_required
def position(key, key2):
    org = utils.organization.get_organization(key)

    pos = Position.query.filter_by(id=key2).first()
    shifts = pos.assigned_shifts.all()
    return render_template('main/position.html', position=pos, organization=org, shifts=shifts)


@main_blueprint.route('/organization/<key>/create_position', methods=['GET', 'POST'])
@login_required
@owns_organization
def create_position(key):
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


@app.route('/assign', methods=['POST'])
@login_required
def assign():
    # get the user
    myuser = User.query.filter_by(id=request.form["assignuserid"]).first_or_404()
    # get the position
    mypos = Position.query.filter_by(title=request.form['position']).first_or_404()
    # get org to redirect back to the previous page
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()
    # if this user already exists return flash
    if myuser in mypos.assigned_users:
        flash('This persons position is already assigned to ' + mypos.title, 'danger')
        return render_template('main/member.html', user=myuser, organization=org)
    # append the assigned_users table
    mypos.assigned_users.append(myuser)
    # commit it to the database
    db.session.commit()
    # redirects to the page before
    return render_template('main/member.html', user=myuser, organization=org)


@app.route('/unassign', methods=['POST'])
@login_required
def unassign():
    # get the user
    myuser = User.query.filter_by(id=request.form["unassignuserid"]).first_or_404()
    # get the position
    mypos = Position.query.filter_by(id=request.form["unassignposid"]).first_or_404()
    # get org to redirect back to the previous page
    org = Organization.query.filter_by(id=request.form["org"]).first_or_404()
    # remove the user from the table
    mypos.assigned_users.remove(myuser)
    # commit the changes to the database
    db.session.commit()
    # redirects to the page before
    return render_template('main/member.html', user=myuser, organization=org)
