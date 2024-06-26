from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_session import Session
from flask_wtf import CSRFProtect
from flask_bootstrap import Bootstrap5

from config import Config

config = Config()

app = Flask(__name__)
app.config.from_object(config)

session = Session()
db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
bootstrap = Bootstrap5()
# csrf._exempt_views.add('dash.dash.dispatch')

lm = LoginManager()
lm.session_protection = None
lm.login_view = "login"
lm.login_message_category = "debug"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SESSION_COOKIE_NAME"] = "pcs_app_session"

session.init_app(app)
lm.init_app(app)
db.init_app(app)
migrate.init_app(app, db)
bootstrap.init_app(app)
csrf.init_app(app)

from app import models, views, api, errors
