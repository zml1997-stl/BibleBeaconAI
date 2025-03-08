import os
import random
import google.generativeai as genai
from sqlalchemy.orm import Session
from models import Verse  # Import Verse directly

# Global variables
_db = None
_model = None

def init(db, api_key):
    """Initialize the verse suggester with database and Gemini API key."""
    global _db, _model
    _db = db
    genai.configure(api_key=api_key)
    _model = genai.GenerativeModel('gemini-2.0-flash')

def get_suggestions(prayer_text, num_suggestions=3):
    """Get verse suggestions for a given prayer text using Gemini."""
    if _db is None or _model is None:
        raise RuntimeError("Verse suggester not initialized. Call init() first.")

    # Fetch all verses from the database
    with Session(_db) as session:
        verses = session.query(Verse).all()  # Use Verse model directly
        verse_texts = [f"{verse.book} {verse.chapter}:{verse.verse_number} - {verse.text}" 
                      for verse in verses]

    # Construct prompt for Gemini
    prompt = (
        f"Given the following prayer: '{prayer_text}', suggest {num_suggestions} "
        "Bible verses that are semantically related. Return only the verse references "
        "(e.g., 'John 3:16') in a list format."
    )

    try:
        # Call Gemini API
        response = _model.generate_content(prompt)
        suggestions_text = response.text.strip()

        # Parse response
        suggested_references = []
        for line in suggestions_text.split('\n'):
            parts = line.split('. ', 1)
            if len(parts) == 2:
                ref = parts[1].strip()
                suggested_references.append(ref)

        # Match references to verse IDs
        suggested_ids = []
        with Session(_db) as session:
            for ref in suggested_references[:num_suggestions]:
                try:
                    book, chap_verse = ref.split(' ', 1)
                    chapter, verse_num = chap_verse.split(':')
                    verse = session.query(Verse).filter_by(
                        book=book, chapter=int(chapter), verse_number=int(verse_num)
                    ).first()
                    if verse:
                        suggested_ids.append(verse.id)
                except (ValueError, AttributeError):
                    continue

        # Fallback to random if needed
        if len(suggested_ids) < num_suggestions:
            with Session(_db) as session:
                all_ids = [v.id for v in session.query(Verse).all()]
                remaining = set(all_ids) - set(suggested_ids)
                suggested_ids.extend(random.sample(list(remaining), 
                                                 min(num_suggestions - len(suggested_ids), len(remaining))))

        return suggested_ids

    except Exception as e:
        print(f"Error with Gemini API: {e}")
        with Session(_db) as session:
            all_ids = [v.id for v in session.query(Verse).all()]
            return random.sample(all_ids, min(num_suggestions, len(all_ids)))