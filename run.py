import os
from dotenv import load_dotenv
from app import create_app, db
from app.models import User, Direction

# Get absolute path to .env file
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'Direction': Direction}

if __name__ == '__main__':
    app.run(debug=True)
