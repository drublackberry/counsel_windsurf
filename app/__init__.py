from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import logging
import sys
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def setup_logging(app):
    """Configure logging for the application"""
    # Create a file handler
    file_handler = logging.FileHandler('app.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter(
        app.config['LOG_FORMAT'],
        datefmt=app.config['LOG_DATE_FORMAT']
    )
    
    # Add formatter to handlers
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Get the root logger and set its level
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # Remove any existing handlers and add our handlers
    root_logger.handlers = []
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)
    
    # Create a logger specific to the app
    logger = logging.getLogger('counsel_windsurf')
    logger.setLevel(logging.DEBUG)
    
    app.logger.handlers = []
    app.logger.addHandler(file_handler)
    app.logger.addHandler(console_handler)
    app.logger.setLevel(logging.DEBUG)
    
    logger.info('Logging setup completed')
    return logger

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Setup logging first
    logger = setup_logging(app)
    logger.info('Creating application instance')

    # Add custom Jinja2 filters
    def nl2br(value):
        if not value:
            return value
        return value.replace('\n', '<br>')
    
    app.jinja_env.filters['nl2br'] = nl2br
    logger.debug('Custom Jinja2 filters added')

    db.init_app(app)
    logger.debug('Database initialized')

    login_manager.init_app(app)
    logger.debug('Login manager initialized')

    migrate.init_app(app, db)
    logger.debug('Database migrations initialized')

    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    logger.debug('Auth blueprint registered')

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)
    logger.debug('Main blueprint registered')

    logger.info('Application instance created successfully')
    return app

from app import models
