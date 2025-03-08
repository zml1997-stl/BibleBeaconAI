import os
import random
from datetime import date
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
db_uri = os.environ.get('DATABASE_URL', 'sqlite:///app.db').replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')

db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, PrivatePrayer, PublicPrayer, Verse
import verse_suggester  # Import as module, not from

verse_suggester.init(db, app.config['GEMINI_API_KEY'])

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    today = date.today()
    random.seed(today.toordinal())
    verses = Verse.query.all()
    verse = random.choice(verses) if verses else None
    return render_template('index.html', verse=verse)

# [Rest of the routes unchanged...]

if __name__ == '__main__':
    app.run(debug=True)