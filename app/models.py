from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login_manager
import numpy as np
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True, nullable=False)
    email = db.Column(db.String(120), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    directions = db.relationship('Direction', backref='author', lazy='dynamic')
    references = db.relationship('Reference', backref='author', lazy='dynamic')
    profiles = db.relationship('UserProfile', backref='author', lazy='dynamic', order_by='UserProfile.timestamp.desc()')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Direction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    embedding = db.Column(db.Text)  # Store embedding as JSON string
    raw_response = db.Column(db.Text)  # Store raw Groq response
    
    # Version control fields
    original_id = db.Column(db.Integer, db.ForeignKey('direction.id'), nullable=True)  # Reference to original direction
    version = db.Column(db.Integer, default=1)  # Version number
    is_latest = db.Column(db.Boolean, default=True)  # Flag for latest version
    previous_versions = db.relationship(
        'Direction',
        backref=db.backref('original', remote_side=[id]),
        foreign_keys=[original_id]
    )

    def set_embedding(self, embedding_array, raw_response=None):
        """Store numpy array as JSON string and raw response"""
        if embedding_array is not None:
            self.embedding = json.dumps(embedding_array.tolist())
        if raw_response is not None:
            self.raw_response = raw_response

    def get_embedding(self):
        """Retrieve embedding as numpy array"""
        if self.embedding:
            return np.array(json.loads(self.embedding))
        return None

    def get_raw_response(self):
        """Retrieve the raw response from Groq"""
        return self.raw_response

class Reference(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    raw_response = db.Column(db.Text)
    embedding = db.Column(db.Text)  # Store embedding as JSON string
    
    def __repr__(self):
        return f'<Reference {self.title}>'
    
    def set_embedding(self, embedding_array):
        """Store numpy array as JSON string."""
        if embedding_array is not None:
            self.embedding = json.dumps(embedding_array.tolist())
    
    def get_embedding(self):
        """Get embedding as numpy array."""
        if self.embedding:
            return np.array(json.loads(self.embedding))
        return None

class UserProfile(db.Model):
    """Stores AI-generated user profiles based on their directions and references."""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<UserProfile {self.author.username} - {self.timestamp}>'

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))
