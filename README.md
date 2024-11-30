# Counsel Windsurf

A Flask-based web application for creating, managing, and finding similar directions using LLM embeddings. The application allows users to create, edit, and search for directions while maintaining semantic similarity using Groq's language model.

## Features

- User Authentication (Register/Login)
- Create and manage directions
- Edit existing directions
- View direction details including raw LLM responses
- Find semantically similar directions using embeddings
- Responsive UI with Bootstrap
- Secure user data handling

## Tech Stack

- **Backend**: Flask 2.0.3
- **Database**: SQLite with SQLAlchemy 1.4.46
- **Authentication**: Flask-Login 0.5.0
- **Forms**: Flask-WTF 1.0.1
- **Database Migrations**: Flask-Migrate 3.1.0
- **LLM Integration**: Groq API
- **Frontend**: Bootstrap, HTML, JavaScript
- **Vector Operations**: NumPy 1.24.3

## Project Structure

```
counsel_windsurf/
├── app/                    # Application package
│   ├── main/              # Main blueprint (routes, forms)
│   ├── templates/         # HTML templates
│   ├── services/          # Service layer (embedding service)
│   └── models.py          # Database models
├── migrations/            # Database migrations
├── config.py             # Configuration settings
├── init_db.py            # Database initialization script
├── run.py                # Application entry point
└── requirements.txt      # Python dependencies
```

## Installation

1. Clone the repository:
```bash
git clone [repository-url]
cd counsel_windsurf
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
Create a `.env` file in the root directory with:
```
FLASK_APP=run.py
GROQ_API_KEY=your_groq_api_key
SECRET_KEY=your_secret_key
```

5. Initialize the database:
```bash
flask db upgrade
python init_db.py
```

## Running the Application

1. Start the development server:
```bash
flask run
```

2. Access the application at `http://localhost:5000`

## Usage

1. **Register/Login**: Create an account or log in to an existing one
2. **Create Direction**: Click "Create New Direction" and fill in the title and description
3. **View Directions**: Browse all directions on the home page
4. **Edit Direction**: Click "Edit Direction" on any direction you own
5. **Find Similar**: View semantically similar directions for any direction
6. **Delete Direction**: Remove directions you've created

## Development

- Database migrations: `flask db migrate -m "Description"`
- Apply migrations: `flask db upgrade`
- Update embeddings: `python update_embeddings.py`

## Environment Variables

- `FLASK_APP`: Application entry point
- `GROQ_API_KEY`: API key for Groq LLM service
- `SECRET_KEY`: Flask secret key for session security

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

[Your chosen license]
