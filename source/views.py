# project/main/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, request, session, g, redirect, url_for
from source import app, db
from flask_login import login_required
from forms import CreateForm

from models import User, Organization


################
#    config    #
################

main_blueprint = Blueprint('main', __name__,)


@app.before_request
def load_user():
    if session["user_id"]:
        user = User.query.filter_by(id=session["user_id"]).first()
    else:
        user = {"name": "Guest"}  # Make it better, use an anonymous User instead

    g.user = user


################
#    routes    #
################

@main_blueprint.route('/')
@login_required
def home():
    return render_template('main/index.html')


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

        return redirect('/organization')


@main_blueprint.route('/organization/<key>', methods=['GET', ])
@login_required
def organization(key):
    org = Organization.query.filter_by(id=key).first()
    return render_template('main/organization.html', organization=org)
