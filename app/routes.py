from flask import render_template
from app import app

# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@app.route('/')
@app.route('/index')
def index():
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
