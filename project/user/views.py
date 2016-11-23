# project/user/views.py


#################
#### imports ####
#################

from flask import render_template, Blueprint, url_for, redirect, flash, request, g, Response
from flask_login import login_user, logout_user, login_required, current_user

from project.models import User, Preference
# from project.email import send_email
from project import db, bcrypt
from .forms import LoginForm, RegisterForm, ChangePasswordForm, PasswordResetEnterEmailForm, PasswordResetEnterPasswordForm
from project import utils
from project.email import ts
from project.utils.token import generate_confirmation_token, confirm_token
import datetime, json
from project.email import send_email
from project.decorators import check_confirmed
################
#### config ####
################

user_blueprint = Blueprint('user', __name__,)


################
#### routes ####
################

@user_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if form.validate_on_submit():
        user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            password=form.password.data,
            confirmed=False,
        )
        db.session.add(user)
        db.session.commit()

        token = generate_confirmation_token(user.email)
        confirm_url = url_for('user.confirm_email', token=token, _external=True)
        html = render_template('user/activate.html', confirm_url=confirm_url)
        subject = "Please confirm your email"
        send_email(user.email, subject, html)

        login_user(user)
        flash('You registered and are now logged in. Welcome!', 'success')

        return redirect(url_for('user.unconfirmed'))

    return render_template('user/register.html', form=form)

@user_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if form.validate_on_submit():
        next = request.args.get('next')
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(
                user.password, request.form['password']):
            login_user(user)
            flash('Welcome.', 'success')
            if next is not None:
                return redirect(next)
            else:
                return redirect(url_for('main.home'))
        else:
            flash('Invalid email and/or password.', 'danger')
            return render_template('user/login.html', form=form)
    return render_template('user/login.html', form=form)


@user_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You were logged out.', 'success')
    return redirect(url_for('user.login'))


@user_blueprint.route('/profile', methods=['GET', 'POST'])
@login_required
@check_confirmed
def profile():
    form = ChangePasswordForm(request.form)
    if form.validate_on_submit():
        user = User.query.filter_by(email=current_user.email).first()
        if user:
            user.password = bcrypt.generate_password_hash(form.password.data)
            db.session.commit()
            flash('Password successfully changed.', 'success')
            return redirect(url_for('user.profile'))
        else:
            flash('Password change was unsuccessful.', 'danger')
            return redirect(url_for('user.profile'))
    return render_template('user/profile.html', form=form)


@user_blueprint.route('/updatepreferences/', methods=['GET', 'POST'])
@login_required
def updatepreferences():
    form = (request.form)
    json_string = json.loads(form['payload'])
    user = User.query.filter_by(email=current_user.email).first()
    user_pref = Preference(
        user_id=user.id,
        start=json_string['start'],
        end=json_string['end'],
    )
    db.session.add(user_pref)
    db.session.commit()
    return 'operation performed'


@user_blueprint.route('/updatepreferences/delete/', methods=['GET', 'POST'])
@login_required
def updatepreferences_delete():
    form = (request.form)
    json_string = json.loads(form['payload'])
    user = User.query.filter_by(email=current_user.email).first()
    selected_preference = Preference.query.filter_by(start=json_string['start'], end=json_string['end'], user_id=user.id).one()
    db.session.delete(selected_preference)
    db.session.commit()
    return 'operation performed'


@user_blueprint.route('/updatepreferences/<key>/', methods=['GET'])
@login_required
def updatepreferences_get_events(key):
    events_list = []
    events = Preference.query.filter_by(user_id=key).all()
    for e in events:                
        events_list.append({'id': e.id,
                            'start': e.start,
                            'end': e.end,
                            })
    json_events_list = json.dumps(events_list)
    response = Response(response=json_events_list,
        status=200,
        mimetype="application/json")
    return response


@user_blueprint.route('/updatepreferences/updateevent/', methods=['GET','POST'])
@login_required
def updatepreferences_update_event():
    form = (request.form)
    json_string = json.loads(form['payload'])
    old_event = Preference.query.filter_by(id=json_string['id']).first()
    old_event.start = json_string['start']
    old_event.end = json_string['end']
    db.session.commit()
    return 'operation performed'

@user_blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash('Account already confirmed. Please login', 'success')
        else:
            user.confirmed = True
            user.confirmed_on = datetime.datetime.now()
            db.session.add(user)
            db.session.commit()
            if g.user is None or g.user.id != user.id:
                login_user(user)
            flash('You have confirmed your account. Thank You!', 'success')
    except:
        flash('The confirmation link is invalid or has expired.', 'danger')
    return redirect(url_for('main.home'))

@user_blueprint.route('/unconfirmed')
@login_required
def unconfirmed():
    if current_user.confirmed:
        return redirect('main.home')
    flash('Please confirm your account!', 'warning')
    return render_template('user/unconfirmed.html')

@user_blueprint.route('/resend')
@login_required
def resend_confirmation():
    token = generate_confirmation_token(current_user.email)
    confirm_url = url_for('user.confirm_email', token=token, _external=True)
    html = render_template('user/activate.html', confirm_url=confirm_url)
    subject = "Please confirm your email"
    send_email(current_user.email, subject, html)
    flash('A new confirmation email has been sent.', 'success')
    return redirect(url_for('user.unconfirmed'))


@user_blueprint.route('/reset_password', methods=['GET', 'POST'])
def request_password_reset():
    form = PasswordResetEnterEmailForm(request.form)
    if form.validate_on_submit():
        utils.organization.send_password_recovery_email(form.email.data)
    return render_template('user/reset_password.html', form=form)    

@user_blueprint.route('/recover_password/<token>', methods=['GET', 'POST'])
def recover_password(token):
    try:
        email = ts.loads(token, salt="recover-key", max_age=86400)
    except:
        flash('Invalid or expired password reset link', 'danger')
        return redirect(url_for('main.landing'))

    form = PasswordResetEnterPasswordForm(request.form)

    if form.validate_on_submit():
        user = User.query.filter_by(email=email).first()

        user.password = bcrypt.generate_password_hash(form.password.data)

        db.session.add(user)
        db.session.commit()
        
        flash('Password successfully reset!', 'success')
        
        return redirect(url_for('main.landing'))

    return render_template('user/reset_with_token.html', form=form, token=token)
