import os
import random
from datetime import date
from flask import Flask, render_template, redirect, url_for, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
db_uri = os.environ.get('DATABASE_URL', 'sqlite:///app.db').replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_uri
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')

# Initialize SQLAlchemy with app
db = SQLAlchemy(app)

# Setup LoginManager
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models and verse suggester
from models import User, PrivatePrayer, PublicPrayer, Verse
from ai import verse_suggester  # Correct import from ai subdirectory

# Initialize verse suggester
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid email or password")
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if User.query.filter_by(email=email).first():
            return render_template('register.html', error="Email already registered")
        user = User(email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('index'))
    return render_template('register.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/prayer_journal')
@login_required
def prayer_journal():
    prayers = PrivatePrayer.query.filter_by(user_id=current_user.id).all()
    return render_template('prayer_journal.html', prayers=prayers)

@app.route('/prayer_journal/new', methods=['POST'])
@login_required
def add_private_prayer():
    text = request.form['text']
    prayer = PrivatePrayer(user_id=current_user.id, text=text)
    db.session.add(prayer)
    db.session.commit()
    suggestions = verse_suggester.get_suggestions(text)
    verses = [Verse.query.get(id) for id in suggestions]
    prayer.verses.extend(verses)
    db.session.commit()
    return redirect(url_for('prayer_journal'))

@app.route('/prayer_wall')
def prayer_wall():
    prayers = PublicPrayer.query.all()
    return render_template('prayer_wall.html', prayers=prayers)

@app.route('/prayer_wall/new', methods=['POST'])
@login_required
def add_public_prayer():
    text = request.form['text']
    prayer = PublicPrayer(user_id=current_user.id, text=text)
    db.session.add(prayer)
    db.session.commit()
    suggestions = verse_suggester.get_suggestions(text)
    verses = [Verse.query.get(id) for id in suggestions]
    prayer.verses.extend(verses)
    db.session.commit()
    return redirect(url_for('prayer_wall'))

@app.route('/pray/<int:prayer_id>', methods=['POST'])
@login_required
def pray(prayer_id):
    prayer = PublicPrayer.query.get_or_404(prayer_id)
    prayer.pray_count += 1
    db.session.commit()
    return jsonify({'pray_count': prayer.pray_count})

if __name__ == '__main__':
    app.run(debug=True)