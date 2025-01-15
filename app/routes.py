from flask import render_template, flash, redirect, url_for
from app import app
from app.forms import LoginForm


# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@app.route('/')
@app.route('/index')
# note that when using url_for(), it will try and find this function view
# and then execute it. So you can get there via a route, or by a url_for()
# however once here, it will take the user to /charlie instead.
# this allows you to change links easily, while maintain connections using url_for()
def bobsanchez():
	# create some mock objects to build a template around
	user = {'username': 'The best girl'}
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
	return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
	form = LoginForm()
	if form.validate_on_submit():
		# flash saves this message in a session backed queue which
		# Jinja can later get with its native get_flashed_messages() function
		# redirect simply redirects
		flash('Login requested for user {}, remember_me={}'.format(form.username.data, form.remember_me.data))
		return redirect(url_for('bobsanchez'))
	return render_template('login.html', title='Sign In', form=form)
