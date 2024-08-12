# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

import os
from typing import Any

from flask import Flask, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from importlib import import_module
from flask_migrate import Migrate
from flask_principal import Principal, Identity,UserNeed, AnonymousIdentity, RoleNeed, identity_loaded, identity_changed
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
from flask_babel import Babel, _, format_datetime, format_currency
import locale
from babel import numbers, Locale
from dotenv import load_dotenv



load_dotenv()
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
principals = Principal()
log = logging
babel = Babel




def register_extensions(app):
    db.init_app(app)
    login_manager.init_app(app)


def register_blueprints(app):
    for module_name in ('authentication', 'home','user','treasurer','account'):
        module = import_module('apps.{}.routes'.format(module_name))
        app.register_blueprint(module.blueprint)


def configure_database(app):

    @app.before_first_request
    def initialize_database():
        try:
            db.create_all()
        except Exception as e:

            print('> Error: DBMS Exception: ' + str(e) )

            # fallback to SQLite
            basedir = os.path.abspath(os.path.dirname(__file__))
            app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite3')

            print('> Fallback to SQLite ')
            db.create_all()

    @app.teardown_request
    def shutdown_session(exception=None):
        db.session.remove()

def get_current_locale_currency(app):
    localeObj = Locale.parse(app.config['BABEL_DEFAULT_LOCALE'])
    return numbers.get_territory_currencies(localeObj.territory)[0]
    
def create_app(config):
    app = Flask(__name__)
    app.logger.info(os.getenv('SECRET_KEY'))
    app.logger.info(os.getenv('BABEL_DEFAULT_LOCALE'))
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    configure_database(app)
    migrate.init_app(app, db)
    principals.init_app(app)
    # app.config['BABEL_TRANSLATION_DIRECTORIES'] = '../translations'  # Directory where translations are stored
    babel = Babel(app)
    locale.setlocale(locale.LC_ALL, app.config['BABEL_DEFAULT_LOCALE']+'.UTF-8')
    # app.logger.setLevel(logging.INFO)
    app.logger.info(app.config)

    # Example context processor
    @app.context_processor
    def inject_common_data():        
        app.logger.info(numbers.format_compact_currency(50000.99,'IDR',fraction_digits=0))
        localeObj = Locale.parse(app.config['BABEL_DEFAULT_LOCALE'])
        app.logger.info(localeObj.territory)
        return {
            'currency': get_current_locale_currency(app),
            'currency_format': app.config['BABEL_DEFAULT_CURRENCY_FORMAT']
    }
    # Locale selector function
    def get_locale():
        app.logger.setLevel(logging.INFO)
        app.logger.info(babel.list_translations())
        app.logger.info(request.args.get('locale_selector'))
        app.logger.info(request.accept_languages)
        app.logger.info(request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'].split(','),'id_ID'))
        # return request.args.get('locale_selector')

        return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'].split(','),'id_ID')
    babel.init_app(app, locale_selector=get_locale)
    app.logger.info('haaa')
    


    def intcomma(value): 
        return "{:,.0f}".format(value)

    def iso8601_to_time(value):
        return datetime.fromisoformat(value) 

    def datetimeformat(value,format):
        return datetime.strftime(value,format)
    def format_datetime_filter(value,format):
        return format_datetime(iso8601_to_time(value),format)    # Register the custom filter
    def format_decimal_custom(number: Any,
        currency: Any,
        format: Any | None = None,
        currency_digits: bool = True,
        format_type: str = 'standard'
        ):
        return numbers.format_currency(number,currency_digits=False,format=app.config['BABEL_DEFAULT_CURRENCY_FORMAT'],currency=get_current_locale_currency(app))
    # numbers.format_compact_currency(number,numbering_system='latn',currency=get_current_locale_currency(app),format_type='short',fraction_digits=0,
                                            #    format=app.config['BABEL_DEFAULT_CURRENCY_FORMAT'])    # Register the custom filter
    app.jinja_env.filters['intcomma'] = intcomma
    app.jinja_env.filters['iso8601_to_time'] = iso8601_to_time
    app.jinja_env.filters['datetimeformat'] = datetimeformat
    app.jinja_env.filters['format_datetime'] = format_datetime_filter
    app.jinja_env.filters['format_currency'] = format_decimal_custom

    
    if app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/app.log', maxBytes=1024000, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('App startup')

    
    
    @identity_loaded.connect_via(app)
    def on_identity_loaded(sender, identity):
        app.logger.info('Identity loaded signal called.')        
        # Set the identity user object
        identity.user = current_user
        app.logger.setLevel(logging.INFO)
        app.logger.info(current_user)
        # Add the UserNeed to the identity
        if hasattr(current_user, 'id'):
            identity.provides.add(UserNeed(current_user.id))

        # Add each role to the identity
        if hasattr(current_user, 'roles'):
            for role in current_user.roles:
                identity.provides.add(RoleNeed(role.name))

    return app
