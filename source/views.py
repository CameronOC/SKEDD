# project/main/views.py

#################
#### imports ####
#################

from flask import render_template, Blueprint, request, session, g, redirect, url_for
from source import app, db
from flask_login import login_required
from forms import CreateForm, ShiftDay

from models import User, Shift, Organization

import datetime

################
#    config    #
################

main_blueprint = Blueprint('main', __name__,)


@app.before_request
def load_user():
    if 'user_id' in session:
        if session["user_id"]:
            user = User.query.filter_by(id=session["user_id"]).first()
        else:
            user = {"email": "Guest"}  # Make it better, use an anonymous User instead
    else:
        user = {"email": "Guest"}  # Make it better, use an anonymous User instead

    g.user = user


################
#    routes    #
################

@main_blueprint.route('/')
def landing():
    return render_template('main/index.html')


@main_blueprint.route('/home', methods=['GET', ])
@login_required
def home():

    orgs = g.user.orgs_owned.all()

    return render_template('main/home.html', organizations=orgs)



@main_blueprint.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    if request.method == 'GET':
        return render_template('main/create.html', form=CreateForm())
    else:
        name = request.form['name']
        owner = g.user

        org = Organization(name=name, owner=owner)

        db.session.add(org)
        db.session.commit()

        return redirect('/organization/' + str(org.id))


@main_blueprint.route('/organization/<key>', methods=['GET', ])
@login_required
def organization(key):
    org = Organization.query.filter_by(id=key).first()

    if org.owner.id != g.user.id:
        return render_template('errors/403_organization.html'), 403

    return render_template('main/organization.html', organization=org)

@main_blueprint.route('/shifts', methods=['GET', 'POST'])
@login_required
def shift():
	if request.method == 'GET':
	    shifts = Shift.query.all()
	    return render_template('main/shifts.html', shifts=shifts, form=ShiftDay())
	else:
		position = request.form['position']			# figure out what to do with this later
		assigned_user_id = g.user.id				# and this
		day = request.form['day']
		start_time = datetime.datetime.strptime(request.form['start_time'], '%H:%M')
		end_time = datetime.datetime.strptime(request.form['end_time'], '%H:%M')
		
		shift = Shift(assigned_user_id=assigned_user_id, day=day, start_time=start_time, end_time=end_time)
		
		db.session.add(shift)
		db.session.commit()
		
		return redirect('/shifts')


