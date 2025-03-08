from flask import Flask, request
from flask_mail import Mail
from flask_moment import Moment
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_babel import Babel, lazy_gettext as _l
import logging
# why is SMTPHandler under logging?
from logging.handlers import SMTPHandler
from logging.handlers import RotatingFileHandler
import os

def get_locale():
    # the languages defined in config.py LANGUAGES also determine what locales are allowed
    return request.accept_languages.best_match(app.config['LANGUAGES'])

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
login.login_view = 'login'
login.login_message = _l('Please log in to access this page.')
mail = Mail(app)
moment = Moment(app)
babel = Babel(app, locale_selector=get_locale)

from app.errors import bp as errors_bp
app.register_blueprint(errors_bp)

from app.auth import bp as auth_bp
app.register_blueprint(auth_bp, url_prefix='/auth')

from app.main import bp as main_bp
app.register_blueprint(main_bp)

# dont run if the app is in debug mode
if not app.debug:
    # if there is a valid mail server
    if app.config['MAIL_SERVER']:
        # set the auth to nothing
        auth = None
        # then if there is at least a username or password filled in for the env variable
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            # change the empty auth flag to a tuple consisting of those variables
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        # set the secure flag to none
        secure = None
        # if the MAIL_USE_TLS is populated, set the secure variable to an empty tuple?? why?
        # empty tuple is used for "yes, but use the defaults"
        if app.config['MAIL_USE_TLS']:
            secure = ()
        # let python "handle" the email using the provided parameters
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs=app.config['ADMINS'], subject='Microblog Failure Notice',
            credentials=auth, secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

from app import models, cli
