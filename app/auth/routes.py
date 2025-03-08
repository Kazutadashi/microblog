from flask import render_template, redirect, url_for, flash, request
from urllib.parse import urlsplit
from flask_login import login_user, logout_user, current_user
from flask_babel import _
import sqlalchemy as sa
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordForm, ResetPasswordRequestForm
from app.models import User
from app.auth.email import send_password_reset_email

@bp.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('main.bobsanchez'))
	form = LoginForm()
	# When "submit" is clicked, it rerurns this route as a POST request, but with validated form input
	# therefore, this function return True, and we continue down this logic
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == form.username.data)
		)
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('main.bobsanchez'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('main.bobsanchez')
		return redirect(url_for('main.bobsanchez'))
	return render_template('login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.bobsanchez'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('main.bobsanchez'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('auth.login'))
	return render_template('register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	if current_user.is_authenticated:
		return redirect(url_for('main.bobsanchez'))
	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.email == form.email.data)
		)
		if user:
			send_password_reset_email(user)
		flash('Check your email for the instructions to reset your password')
		return redirect(url_for('auth.login'))
	return render_template('reset_password_request.html', title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	if current_user.is_authenticated:
		return redirect(url_for('main.bobsanchez'))
	user = User.verify_reset_password_token(token)
	if not user:
		return redirect(url_for('main.bobsanches'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.session.commit()
		flash('Your password has been reset.')
		return redirect(url_for('auth.login'))
	return render_template('reset_password.html', form=form)
