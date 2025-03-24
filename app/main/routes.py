from flask import render_template, flash, redirect, url_for, request, g, current_app
from app import db
from app.main import bp
from app.main.forms import MessageForm
from app.translate import translate
from app.models import User, Post, Message
from app.main.forms import EditProfileForm, EmptyForm, PostForm, SearchForm
import sqlalchemy as sa
from flask_login import current_user, login_required
from datetime import datetime, timezone
from flask_babel import _, get_locale
from langdetect import detect, LangDetectException

@bp.before_request
def before_request():
	if current_user.is_authenticated:
		current_user.last_seen = datetime.now(timezone.utc)
		db.session.commit()
		g.search_form = SearchForm()
	g.locale = str(get_locale())

# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods = ['GET', 'POST'])
@login_required
# note that when using url_for(), it will try and find this function view
# and then execute it. So you can get there via a route, or by a url_for()
# however once here, it will take the user to /charlie instead.
# this allows you to change links easily, while maintain connections using url_for()
def bobsanchez():
	form = PostForm()
	if form.validate_on_submit():
		try:
			language = detect(form.post.data)
		except LangDetectException:
			language = ''
		post = Post(body=form.post.data, author=current_user, language=language)
		db.session.add(post)
		db.session.commit()
		flash(_('Your post is now live!')) # the _() function is used to mark something for translation
		# when submitting data, it is good practice to redirect to the same location
		# after a post request. This removes strange reloading behavior, since it performs a GET
		# and makes a GET the last response. This is called the "POST/Redirect/GET pattern
		# and helps prevent duplicated data
		return redirect(url_for('main.bobsanchez'))

	page = request.args.get('page', 1, type=int)
	posts = db.paginate(current_user.following_posts(), page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	next_url = url_for('main.bobsanchez', page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.bobsanchez', page=posts.prev_num) if posts.has_prev else None
	# templates are the actual html documents, and they must be rendered
	# to be visible tok the user. When we direct user to a function view
	# the view can try and load a template to provide to the user through
	# the render template function
	return render_template('index.html', title='Home', posts=posts, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>')
@login_required
def user(username):
	user = db.first_or_404(sa.select(User).where(User.username == username))
	page = request.args.get('page', 1, type=int)
	query = user.posts.select().order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	next_url = url_for('main.user', username=user.username, page=posts.next_num) if posts.has_next else None
	prev_url = url_for('main.user', username=user.username, page=posts.prev_num) if posts.has_prev else None
	form = EmptyForm()
	return render_template('user.html', user=user, posts=posts.items, form=form, next_url=next_url, prev_url=prev_url)

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your changes have been saved.')
		return redirect(url_for('main.edit_profile'))
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
@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username)
		)
		if user is None:
			# here we can see an example of old formatting style for babel
			flash(_('User %(username)s not found.', username=username))
			return redirect(url_for('main.bobsanchez'))
		if user == current_user:
			flash('You cannot follow yourself!')
			return redirect(url_for('main.user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash(f'You are now following {username}!')
		return redirect(url_for('main.user', username=username))
	else:
		return redirect(url_for('main.index'))

@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username)
		)
		if user is None:
			flash(f'User {username} not found.')
			return redirect(url_for('main.bobsanchez'))
		if user == current_user:
			flash('You cannot unfollow yourself!')
			return redirect(url_for('main.user', username=username))
		current_user.unfollow(user)
		db.session.commit()
		flash(f'You are not following {username}.')
		return redirect(url_for('main.user', username=username))
	else:
		return redirect(url_for('main.bobsanchez'))

@bp.route('/explore')
@login_required
def explore():
	page = request.args.get('page', 1, type=int)
	query = sa.select(Post).order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)

	return render_template('index.html', title='Explore', posts=posts.items)

@bp.route('/translate', methods=['POST'])
@login_required
def translate_text():
	data = request.get_json()
	return {'text': translate(data['text'], data['source_language'], data['dest_language'])}


@bp.route('/search')
@login_required
def search():
	if not g.search_form.validate():
		return redirect(url_for('main.explore'))
	page = request.args.get('page', 1, type=int)
	posts, total = Post.search(g.search_form.q.data, page,
							   current_app.config['POSTS_PER_PAGE'])
	next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
		if total > page * current_app.config['POSTS_PER_PAGE'] else None
	prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
		if page > 1 else None
	return render_template('search.html', title=_('Search'), posts=posts,
						   next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>/popup')
@login_required
def user_popup(username):
	user = db.first_or_404(sa.select(User).where(User.username == username))
	form = EmptyForm()
	return render_template('user_popup.html', user=user, form=form)

@bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
@login_required
def send_message(recipient):
	user = db.first_or_404(sa.select(User).where(User.username == recipient))
	form = MessageForm()
	if form.validate_on_submit():
		msg = Message(author=current_user, recipient=user, body=form.message.data)
		db.session.add(msg)
		db.session.commit()
		flash(_('Your message has been sent.'))
		return redirect(url_for('main.user', username=recipient))
	return render_template('send_message.html', title=_('Send Message'),
						   form=form, recipient=recipient)

@bp.route('/messages')
@login_required
def messages():
	current_user.last_message_read_time = datetime.now(timezone.utc)
	db.session.commit()
	page = request.args.get('page', 1, type=int)
	query = current_user.messages_received.select().order_by(
		Message.timestamp.desc()
	)
	messages = db.paginate(query, page=page, per_page=current_app.config['POSTS_PER_PAGE'],
						   error_out=False)
	next_url = url_for('main.messages', page=messages.next_num) if messages.has_next else None
	prev_url = url_for('main.messages', page=messages.prev_num) if messages.has_prev else None
	return render_template('messages.html', messages=messages.items, next_url=next_url, prev_url=prev_url)