from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# SQLAlchemy instance is imported from app.py, so we don't initialize it here
db = SQLAlchemy()

# Association table for verse suggestions (many-to-many relationship)
private_prayer_verses = db.Table(
    'private_prayer_verses',
    db.Column('prayer_id', db.Integer, db.ForeignKey('private_prayers.id'), primary_key=True),
    db.Column('verse_id', db.Integer, db.ForeignKey('verses.id'), primary_key=True)
)

public_prayer_verses = db.Table(
    'public_prayer_verses',
    db.Column('prayer_id', db.Integer, db.ForeignKey('public_prayers.id'), primary_key=True),
    db.Column('verse_id', db.Integer, db.ForeignKey('verses.id'), primary_key=True)
)

class User(UserMixin, db.Model):
    """User model for authentication."""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    # Relationships
    private_prayers = db.relationship('PrivatePrayer', backref='user', lazy=True)
    public_prayers = db.relationship('PublicPrayer', backref='user', lazy=True)

    def set_password(self, password):
        """Set hashed password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password_hash, password)

class PrivatePrayer(db.Model):
    """Model for private prayer journal entries."""
    __tablename__ = 'private_prayers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    
    # Many-to-many relationship with verses
    verses = db.relationship('Verse', secondary=private_prayer_verses, lazy='subquery')

class PublicPrayer(db.Model):
    """Model for public prayer wall entries."""
    __tablename__ = 'public_prayers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=db.func.now())
    pray_count = db.Column(db.Integer, default=0)
    
    # Many-to-many relationship with verses
    verses = db.relationship('Verse', secondary=public_prayer_verses, lazy='subquery')

class Verse(db.Model):
    """Model for Bible verses."""
    __tablename__ = 'verses'
    
    id = db.Column(db.Integer, primary_key=True)
    book = db.Column(db.String(50), nullable=False)
    chapter = db.Column(db.Integer, nullable=False)
    verse_number = db.Column(db.Integer, nullable=False)
    text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"{self.book} {self.chapter}:{self.verse_number} - {self.text[:50]}..."
