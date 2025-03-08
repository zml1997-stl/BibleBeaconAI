from app import app, db
from utils import import_verses

def init_db():
    with app.app_context():
        print("App context entered")
        db.create_all()
        print("Database tables created successfully")
        import_verses()
        print("Initialization complete")

if __name__ == '__main__':
    try:
        init_db()
    except Exception as e:
        print(f"Error initializing database: {e}")
        raise