import sqlalchemy as sa
import sqlalchemy.orm as so
from app import app, db
from app.models import User, Post

print('We have loaded the app via microblog.py successfully')
@app.shell_context_processor
def make_shell_context():
    return {'sa': sa, 'so': so, 'db': db, 'User': User, 'Post': Post}

