from app import app, db
from utils import import_verses

def init_db():
    """Initialize the database and import verses."""
    with app.app_context():
        db.create_all()
        print("Database tables created successfully.")
        import_verses()

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise