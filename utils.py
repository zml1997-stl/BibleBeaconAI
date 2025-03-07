import csv
import os
from models import db, Verse

def import_verses(file_path='data/verses.csv'):
    """
    Import Bible verses from a CSV file into the database.
    Expected CSV format: book,chapter,verse_number,text
    """
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} not found.")
        return

    # Check if verses already exist to avoid duplicates
    if Verse.query.first():
        print("Database already contains verses. Skipping import.")
        return

    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if not all(col in reader.fieldnames for col in ['book', 'chapter', 'verse_number', 'text']):
                print("Error: CSV file must contain 'book', 'chapter', 'verse_number', and 'text' columns.")
                return

            verses = []
            for row in reader:
                verse = Verse(
                    book=row['book'],
                    chapter=int(row['chapter']),
                    verse_number=int(row['verse_number']),
                    text=row['text']
                )
                verses.append(verse)

            # Bulk insert for efficiency
            db.session.bulk_save_objects(verses)
            db.session.commit()
            print(f"Successfully imported {len(verses)} verses into the database.")
    except Exception as e:
        db.session.rollback()
        print(f"Error importing verses: {e}")

if __name__ == '__main__':
    # Example usage: run this file directly to import verses
    import_verses()
