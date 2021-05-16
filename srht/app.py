from flask import Flask, render_template, request, g, Response, redirect, url_for
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from jinja2 import FileSystemLoader, ChoiceLoader

import random
import sys
import os
import locale

from srht.config import _cfg, _cfgi
from srht.database import db, init_db
from srht.objects import User
from srht.common import *
from srht.network import *

from srht.blueprints.html import html
from srht.blueprints.api import api
from srht.blueprints.oauth import oauth

app = Flask(__name__)
csrf = CSRFProtect()
csrf.init_app(app)
app.secret_key = _cfg("secret-key")
app.jinja_env.cache = None
init_db()
login_manager = LoginManager()
login_manager.init_app(app)

app.jinja_loader = ChoiceLoader([
    FileSystemLoader("overrides"),
    FileSystemLoader("templates"),
])

@login_manager.user_loader
def load_user(username):
    return User.query.filter(User.username == username).first()

login_manager.anonymous_user = lambda: None

app.register_blueprint(html)
app.register_blueprint(api)
app.register_blueprint(oauth)

try:
    locale.setlocale(locale.LC_ALL, 'en_US')
except:
    pass

if not app.debug:
    @app.errorhandler(500)
    def handle_500(e):
        # shit
        try:
            db.rollback()
            db.close()
        except:
            # shit shit
            sys.exit(1)
        return render_template("internal_error.html"), 500
    # Error handler
    if _cfg("error-to") != "":
        import logging
        from logging.handlers import SMTPHandler
        mail_handler = SMTPHandler((_cfg("smtp-host"), _cfg("smtp-port")),
           _cfg("error-from"),
           [_cfg("error-to")],
           'sr.ht application exception occured',
           credentials=(_cfg("smtp-user"), _cfg("smtp-password")))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

@app.errorhandler(404)
def handle_404(e):
    return render_template("not_found.html"), 404

moe = os.listdir('_static/moe/')

@app.context_processor
def inject():
    return {
        'root': _cfg("protocol") + "://" + _cfg("domain"),
        'domain': _cfg("domain"),
        'protocol': _cfg("protocol"),
        'len': len,
        'any': any,
        'request': request,
        'locale': locale,
        'url_for': url_for,
        'file_link': file_link,
        'disown_link': disown_link,
        'user': current_user,
        'moe': random.choice(moe),
        'random': random,
        'owner': _cfg("owner"),
        'owner_email': _cfg("owner_email"),
        '_cfg': _cfg
    }
