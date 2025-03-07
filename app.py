import os
import random
from datetime import date
from flask import Flask, render_template, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user, login_user, logout_user, login_required

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://localhost/christian_ai')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'default-secret-key')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Import models and AI verse suggester
from models import User, PrivatePrayer, PublicPrayer, Verse
from ai import verse_suggester

# Initialize verse suggester with database and Gemini API key
app.config['GEMINI_API_KEY'] = os.environ.get('GEMINI_API_KEY', 'your-gemini-api-key-here')
verse_suggester.init(db, app.config['GEMINI_API_KEY'])

@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login."""
    return User.query.get(int(user_id))

@app.route('/')
def index():
    """Display homepage with daily Bible verse."""
    # Use date-based seeding for consistent daily verse
    today = date.today()
    random.seed(today.toordinal())
    verse = random.choice(Verse.query.all())
    return render_template('index.html', verse=verse)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
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
    """Handle user registration."""
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
    """Log out the user."""
    logout_user()
    return redirect(url_for('index'))

@app.route('/prayer_journal')
@login_required
def prayer_journal():
    """Display user's private prayer journal."""
    prayers = PrivatePrayer.query.filter_by(user_id=current_user.id).all()
    return render_template('prayer_journal.html', prayers=prayers)

@app.route('/prayer_journal/new', methods=['POST'])
@login_required
def add_private_prayer():
    """Add a new private prayer with AI-suggested verses."""
    text = request.form['text']
    prayer = PrivatePrayer(user_id=current_user.id, text=text)
    db.session.add(prayer)
    db.session.commit()
    # Get verse suggestions using Gemini
    suggestions = verse_suggester.get_suggestions(text)
    verses = [Verse.query.get(id) for id in suggestions]
    prayer.verses.extend(verses)
    db.session.commit()
    return redirect(url_for('prayer_journal'))

@app.route('/prayer_wall')
def prayer_wall():
    """Display public prayer wall."""
    prayers = PublicPrayer.query.all()
    return render_template('prayer_wall.html', prayers=prayers)

@app.route('/prayer_wall/new', methods=['POST'])
@login_required
def add_public_prayer():
    """Add a new public prayer with AI-suggested verses."""
    text = request.form['text']
    prayer = PublicPrayer(user_id=current_user.id, text=text)
    db.session.add(prayer)
    db.session.commit()
    # Get verse suggestions using Gemini
    suggestions = verse_suggester.get_suggestions(text)
    verses = [Verse.query.get(id) for id in suggestions]
    prayer.verses.extend(verses)
    db.session.commit()
    return redirect(url_for('prayer_wall'))

@app.route('/pray/<int:prayer_id>', methods=['POST'])
@login_required
def pray(prayer_id):
    """Increment pray count for a public prayer."""
    prayer = PublicPrayer.query.get_or_404(prayer_id)
    prayer.pray_count += 1
    db.session.commit()
    return {'pray_count': prayer.pray_count}  # For AJAX response

if __name__ == '__main__':
    app.run(debug=True)
