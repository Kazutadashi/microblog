from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm
from app.models import User
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit

# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@app.route('/')
@app.route('/index')
@login_required
# note that when using url_for(), it will try and find this function view
# and then execute it. So you can get there via a route, or by a url_for()
# however once here, it will take the user to /charlie instead.
# this allows you to change links easily, while maintain connections using url_for()
def bobsanchez():
	# create some mock objects to build a template around
	posts = [
		{
			'author': {'username': 'Owen'},
			'body': 'Evelyn is the best',
		},
		{
			'author': {'username': 'Evelyn'},
			'body': 'Fun day with Owen in Moab!',
		},
		{
			'author': {'username': 'Owen'},
			'body': 'I agree with Evelyn!!',
		}
	]

	# templates are the actual html documents, and they must be rendered
	# to be visible tok the user. When we direct user to a function view
	# the view can try and load a template to provide to the user through
	# the render template function
	return render_template('index.html', title='Home', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('bobsanchez'))
	form = LoginForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == form.username.data)
		)
		if user is None or not user.check_password(form.password.data):
			flash('Invalid username or password')
			return redirect(url_for('bobsanchez'))
		login_user(user, remember=form.remember_me.data)
		next_page = request.args.get('next')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('bobsanchez')
		return redirect(url_for('bobsanchez'))
	return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('bobsanchez'))