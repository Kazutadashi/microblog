from app import app

# This is called a route. Routes are responsible for determining
# what happens when a visitor goes to a specific place on your website
# The function below is called the "view function", which in this case is pretty simple
@app.route('/')
@app.route('/index')
def index():
	return "Hello, world!"
