from app import app, db
from utils import import_verses

try:
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
        import_verses()
except Exception as e:
    print(f"Error initializing database: {e}")
    raise