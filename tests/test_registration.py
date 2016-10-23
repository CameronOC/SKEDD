from flask_testing import TestCase

from project import app, db
from project.models import User
from project.user.forms import RegisterForm, LoginForm, ChangePasswordForm
from project.utils.token import generate_confirmation_token, confirm_token, generate_invitation_token, confirm_invitation_token
import datetime


class BaseTestCase(TestCase):

    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        user = User(
            email='ad@min.com',
            first_name='local',
            last_name='admin',
            password='admin_user',
            confirmed=True
        )
        db.session.add(user)
        user1 = User(
            email='test@user.com',
            first_name='test',
            last_name='test',
            password='test_user',
            confirmed=False
        )
        db.session.add(user1)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_check_success_register_form(self):
        """
        Test that correct data lets a user register
        """
        form = RegisterForm(
            email='new@test.test',
            password='example',
            first_name='test',
            last_name='test',
            confirm='example')
        self.assertTrue(form.validate())

    def test_check_invalid_password_format(self):
        """
        Test Check that incorrect data does not let a user register
        """
        form = RegisterForm(
            first_name = 'test',
            last_name = 'test',
            email='new@test.test',
            password='example',
            confirm='wrong')
        self.assertFalse(form.validate())

    def test_check_email_already_registered(self):
        """
        Tests that user can't register with a email that is already being used
        """
        form = RegisterForm(
            first_name = 'test',
            last_name = 'test',
            email='ad@min.com',
            password='just_a_test_user',
            confirm='just_a_test_user'
        )
        self.assertFalse(form.validate())

    def test_check_login(self):
        """
        Tests if user can login with valid info
        """
        form = LoginForm(email='ad@min.com', password='admin_user')
        self.assertTrue(form.validate())

    def test_check_invalid_email(self):
        """
        Tests that if wrong email and password user can't log in
        """
        form = LoginForm(email='unknown', password='unkown')
        self.assertFalse(form.validate())

    def test_check_success_change_password(self):
        """
        Tests that correct data changes the password.
        """
        form = ChangePasswordForm(password='update', confirm='update')
        self.assertTrue(form.validate())

    def test_check_invalid_change_password(self):
        """
        Tests that passwords must match when chaning password
        """
        form = ChangePasswordForm(password='update', confirm='unknown')
        self.assertFalse(form.validate())

    def test_check_invalid_change_password_format(self):
        """
        Tests that invalid password format throws error.
        """
        form = ChangePasswordForm(password='123', confirm='123')
        self.assertFalse(form.validate())

    def test_confirm_token_route_valid_token(self):
        """
        Tests user can confirm account with valid token.
        :return:
        """
        with self.client:
            self.client.post('/login', data=dict(
                email='test@user.com', password='test_user'
            ), follow_redirects=True)
            token = generate_confirmation_token('test@user.com')
            response = self.client.get('/confirm/'+token, follow_redirects=True)
            self.assertIn(b'You have confirmed your account. Thank You!', response.data)
            self.assertTemplateUsed('main/home.html')
            user = User.query.filter_by(email='test@user.com').first_or_404()
            self.assertIsInstance(user.confirmed_on, datetime.datetime)
            self.assertTrue(user.confirmed)

    def test_confirm_token_route_invalid_token(self):
        """
        Tests user cannot confirm account with invalid token.
        :return:
        """
        token = generate_confirmation_token('test@test1.com')
        with self.client:
            self.client.post('/login', data=dict(
                email='test@user.com', password='test_user'
            ), follow_redirects=True)
            response = self.client.get('/confirm/'+token, follow_redirects=True)
            self.assertIn(
                b'The confirmation link is invalid or has expired.',
                response.data
            )

    def test_confirm_token_route_expired_token(self):
        """
        Tests user cannot confirm account with expired token.
        """
        user = User(email='test@test1.com', password='test1', first_name='test', last_name='test', confirmed=False)
        db.session.add(user)
        db.session.commit()
        token = generate_confirmation_token('test@test1.com')
        self.assertFalse(confirm_token(token, -1))

    def test_confirm_invite_token_route_valid_token(self):
        """
        Tests user can confirm account with valid token.
        :return:
        """
        with self.client:
            self.client.post('/login', data=dict(
                email='test@user.com', password='test_user'
            ), follow_redirects=True)
            token = generate_invitation_token('test@user.com')
            response = self.client.get('/confirm/'+token, follow_redirects=True)
            self.assertIn(b'You have confirmed your account. Thank You!', response.data)
            self.assertTemplateUsed('main/home.html')
            user = User.query.filter_by(email='test@user.com').first_or_404()
            self.assertIsInstance(user.confirmed_on, datetime.datetime)
            self.assertTrue(user.confirmed)

    def test_confirm_invite_token_route_invalid_token(self):
        """
        Tests user cannot confirm account with invalid invitation token.
        :return:
        """
        token = generate_invitation_token('test@test2.com')
        with self.client:
            self.client.post('/login', data=dict(
                email='test@user.com', password='test_user'
            ), follow_redirects=True)
            response = self.client.get('/confirm/'+token, follow_redirects=True)
            self.assertIn(
                b'The confirmation link is invalid or has expired.',
                response.data
            )

    def test_confirm_invite_token_route_expired_token(self):
        """
        Tests user cannot confirm account with expired invitation token.
        """
        user = User(email='test@test5.com', password='test5', first_name='test', last_name='test', confirmed=False)
        db.session.add(user)
        db.session.commit()
        token = generate_invitation_token('test@test5.com')
        self.assertFalse(confirm_invitation_token(token, -1))

