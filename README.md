# Campfire 🔥

A Flask-based web application for personal growth tracking and mentoring, powered by AI. The application helps users explore growth directions and find meaningful references while maintaining semantic understanding through advanced embedding techniques.

## Features

- 👤 User Authentication (Register/Login)
- 📈 Create and manage growth directions
- 📚 Store and manage references
- 💬 Interactive AI conversations for growth exploration
- 🔍 Find semantically similar content using embeddings
- 📊 View conversation history and AI responses
- 🎯 Track personal growth journey
- 🏥 Monitor external service health
- 🔒 Secure user data handling
- 📱 Responsive UI with Bootstrap

## Tech Stack

- **Backend**: Flask 2.0.3
- **Database**: SQLite with SQLAlchemy 1.4.46
- **Authentication**: Flask-Login 0.5.0
- **Forms**: Flask-WTF 1.0.1
- **Database Migrations**: Flask-Migrate 3.1.0
- **AI Integration**: 
  - Groq API (Mixtral-8x7b) for conversations
  - HuggingFace Sentence Transformers for embeddings
- **Frontend**: Bootstrap 5, HTML, JavaScript
- **Vector Operations**: NumPy 1.24.3

## Project Structure

```
campfire/
├── app/                    # Application package
│   ├── main/              # Main blueprint (routes, forms)
│   ├── templates/         # HTML templates
│   ├── services/          # Service layer (chat, embedding services)
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
cd campfire
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
FLASK_ENV=development
GROQ_API_KEY=your_groq_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key
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

1. **Register/Login**: Create an account or log in
2. **Growth Directions**: 
   - Create new growth directions through AI conversations
   - View and manage your growth journey
   - Find similar directions for inspiration
3. **References**:
   - Store important references and learnings
   - Connect references to your growth directions
   - Find related references through semantic search
4. **Health Monitoring**:
   - Check service status at `/health`
   - Monitor Groq and HuggingFace API connectivity
   - View detailed health metrics with visual indicators

## Development

- Database migrations: `flask db migrate -m "Description"`
- Apply migrations: `flask db upgrade`
- Health check: Visit `/health` endpoint
- Update embeddings: `python update_embeddings.py`

## Environment Variables

- `FLASK_APP`: Application entry point
- `FLASK_ENV`: Development environment
- `GROQ_API_KEY`: API key for Groq's Mixtral-8x7b model
- `HUGGINGFACE_API_KEY`: API key for HuggingFace's services
- `SECRET_KEY`: Flask application secret key

## Service Health Monitoring

The application includes a comprehensive health monitoring system:

- **Endpoint**: `/health`
- **Features**:
  - Real-time status of all external services
  - Visual health indicators with emojis
  - Detailed error messages
  - Automatic startup health check
  - Refresh capability for latest status

## Recent Updates

- 🆕 Added HuggingFace embedding service integration
- 🆕 Implemented semantic similarity search
- 🆕 Added comprehensive health monitoring system
- 🆕 Enhanced logging with emoji indicators
- 🆕 Improved error handling and recovery
