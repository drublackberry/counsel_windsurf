import os
import sys
from app import create_app, db
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    try:
        app = create_app()
        with app.app_context():
            # Check if database file exists and remove it if it does
            db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
            if os.path.exists(db_path):
                logger.info(f"Removing existing database at {db_path}")
                os.remove(db_path)
            
            # Create all tables
            logger.info("Creating database tables...")
            db.create_all()
            
            # Initialize migrations
            logger.info("Initializing migrations...")
            from flask_migrate import upgrade, current, init, stamp
            migrations_dir = os.path.join(os.path.dirname(__file__), 'migrations')
            
            if not os.path.exists(migrations_dir):
                init()
            
            # Create tables and stamp the migration
            db.create_all()
            stamp()
            
            logger.info("Database initialized successfully!")
            return True
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False

if __name__ == '__main__':
    success = init_db()
    sys.exit(0 if success else 1)
