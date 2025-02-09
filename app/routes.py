from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Post
from app.forms import RegistrationForm, EditProfileForm, EmptyForm, PostForm
import sqlalchemy as sa
from flask_login import current_user, login_user, logout_user, login_required
from urllib.parse import urlsplit
from datetime import datetime, timezone


@app.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now(timezone.utc)
		db.session.commit()


# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods = ['GET', 'POST'])
@login_required
# note that when using url_for(), it will try and find this function view
# and then execute it. So you can get there via a route, or by a url_for()
# however once here, it will take the user to /charlie instead.
# this allows you to change links easily, while maintain connections using url_for()
def bobsanchez():
	form = PostForm()
	if form.validate_on_submit():
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash('Your post is now live!')
		# when submitting data, it is good practice to redirect to the same location
		# after a post request. This removes strange reloading behavior, since it performs a GET
		# and makes a GET the last response. This is called the "POST/Redirect/GET pattern
		# and helps prevent duplicated data
		return redirect(url_for('bobsanchez'))

	page = request.args.get('page', 1, type=int)
	posts = db.paginate(current_user.following_posts(), page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)
	next_url = url_for('bobsanchez', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('bobsanchez', page=posts.prev_num) if posts.has_prev else None
	# templates are the actual html documents, and they must be rendered
	# to be visible tok the user. When we direct user to a function view
	# the view can try and load a template to provide to the user through
	# the render template function
	return render_template('index.html', title='Home', posts=posts, form=form)


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


@app.route('/register', methods=['GET', 'POST'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('bobsanchez'))
	form = RegistrationForm()
	if form.validate_on_submit():
		user = User(username=form.username.data, email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>')
@login_required
def user(username):
	user = db.first_or_404(sa.select(User).where(User.username == username))
	posts = [
		{'author': user, 'body': 'Test post #1'},
		{'author': user, 'body': 'Test post #2'}
	]
	form = EmptyForm()
	return render_template('user.html', user=user, posts=posts, form=form)

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('edit_profile'))
	# when a user simply just visits this page, it becomes a GET request
	# so this part of the code runs instead of the POST part
	elif request.method == 'GET':
		# this fills the form data automatically with what existed in the database
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', form=form)

# These aren't really "real" routes. Its more of a method to route the user to some specific logic
# This route also redirects the user in every situation, so you never see this page. It just performs its logics
# and then goes back to something specific.
@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username)
		)
		if user is None:
			flash(f'User {username} not found.')
			return redirect(url_for('bobsanchez'))
		if user == current_user:
			flash('You cannot follow yourself!')
			return redirect(url_for('user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash(f'You are now following {username}!')
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('index'))

@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username)
		)
		if user is None:
			flash(f'User {username} not found.')
			return redirect(url_for('bobsanchez'))
		if user == current_user:
			flash('You cannot unfollow yourself!')
			return redirect(url_for('user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash(f'You are not following {username}.')
		return redirect(url_for('user', username=username))
	else:
		return redirect(url_for('bobsanchez'))

@app.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	query = sa.select(Post).order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page, per_page=app.config['POSTS_PER_PAGE'], error_out=False)

	return render_template('index.html', title='Explore', posts=posts.items)
