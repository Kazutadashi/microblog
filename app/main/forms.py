from flask_wtf import FlaskForm
from flask import request
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, ValidationError, Length
import sqlalchemy as sa
from app import db
from app.models import User

class EditProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('Submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    # this function is called by Flask-WTF anytime submit is used as a POST request
    # this runs after all the other validators we've defined earlier.
    def validate_username(self, username):
        if username.data != self.original_username:
            user = db.session.scalar(sa.select(User).where(
                User.username == username.data
            ))
            if user is not None:
                raise ValidationError("Please use a different username.")

class EmptyForm(FlaskForm):
    submit = SubmitField('Submit')

class PostForm(FlaskForm):
    post = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    q = StringField(_l('Search'), validators=[DataRequired()])

    def __init__(self, *args, **kwargs):
        if 'formdata' not in kwargs:
            kwargs['formdata'] = request.args
        if 'meta' not in kwargs:
            kwargs['meta'] = {'csrf': False}
        super(SearchForm, self).__init__(*args, **kwargs)

class MessageForm(FlaskForm):
    message = TextAreaField(_l('Message'), validators=[DataRequired(), Length(min=0, max=140)])
    submit = SubmitField(_l('Submit'))

