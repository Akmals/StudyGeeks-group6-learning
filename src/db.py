"""
db.py
StudyGeeks -- Database Helper Module
Author: Akmal
Sprint 2

Wraps every SQLite operation into simple, readable functions so that
other modules (quiz_mode.py, future modules) never have to write raw SQL.

Usage:
    import db

    db.init()                              # Set up tables (call once at startup)
    decks = db.get_all_decks()             # -> list of dicts
    cards = db.get_cards_for_deck(deck_id) # -> list of dicts
    db.add_deck("Python Basics", "CS")     # -> new deck_id (int)
    db.add_card(deck_id, "Q?", "A")        # -> new card_id (int)
    db.save_quiz_result(deck_id, 10, 8, 2)
    history = db.get_quiz_history(deck_id) # -> list of dicts
    db.delete_deck(deck_id)
    db.delete_card(card_id)
"""

import sqlite3
import os

# ── Path to the database file ────────────────────────────────────────────────
# Stored in the data/ directory at the project root so it's easy to find.
_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(_BASE_DIR, "data", "studygeeks.db")


# ── Internal connection helper ───────────────────────────────────────────────

def _get_conn():
    """
    Open and return a new SQLite connection.
    row_factory makes every row accessible as a dict (row["column_name"]).
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # lets callers use row["name"]
    conn.execute("PRAGMA foreign_keys = ON") # enforce FK constraints
    return conn


# ── Table setup ─────────────────────────────────────────────────────────────

def init():
    """
    Create all required tables if they don't already exist.
    Call this once when the application starts.
    """
    with _get_conn() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS decks (
                id      INTEGER PRIMARY KEY AUTOINCREMENT,
                name    TEXT    NOT NULL,
                subject TEXT
            );

            CREATE TABLE IF NOT EXISTS cards (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id  INTEGER NOT NULL,
                question TEXT    NOT NULL,
                answer   TEXT    NOT NULL,
                FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS quiz_results (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                deck_id     INTEGER NOT NULL,
                total_cards INTEGER NOT NULL,
                correct     INTEGER NOT NULL,
                incorrect   INTEGER NOT NULL,
                timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (deck_id) REFERENCES decks(id) ON DELETE CASCADE
            );
        """)


# ── Deck functions ───────────────────────────────────────────────────────────

def get_all_decks():
    """
    Return every deck as a list of dicts with keys: id, name, subject.

    Example:
        [{"id": 1, "name": "Python Basics", "subject": "CS"}, ...]
    """
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, name, subject FROM decks ORDER BY name"
        ).fetchall()
    return [dict(r) for r in rows]


def get_deck(deck_id):
    """
    Return a single deck dict (id, name, subject) or None if not found.
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, name, subject FROM decks WHERE id = ?", (deck_id,)
        ).fetchone()
    return dict(row) if row else None


def add_deck(name, subject=None):
    """
    Insert a new deck and return its new id.

    Args:
        name (str):    Deck title, e.g. "Python Basics"
        subject (str): Optional subject label, e.g. "Computer Science"

    Returns:
        int: The id of the newly created deck.
    """
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO decks (name, subject) VALUES (?, ?)", (name, subject)
        )
        return cursor.lastrowid


def update_deck(deck_id, name=None, subject=None):
    """
    Update the name and/or subject of an existing deck.
    Only the fields you pass in will be changed.

    Args:
        deck_id (int): The deck to update.
        name (str):    New deck name (optional).
        subject (str): New subject label (optional).
    """
    fields, values = [], []
    if name is not None:
        fields.append("name = ?")
        values.append(name)
    if subject is not None:
        fields.append("subject = ?")
        values.append(subject)
    if not fields:
        return  # nothing to update
    values.append(deck_id)
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE decks SET {', '.join(fields)} WHERE id = ?", values
        )


def delete_deck(deck_id):
    """
    Delete a deck and all its cards / quiz results (cascades automatically).

    Args:
        deck_id (int): The deck to remove.
    """
    with _get_conn() as conn:
        conn.execute("DELETE FROM decks WHERE id = ?", (deck_id,))


# ── Card functions ───────────────────────────────────────────────────────────

def get_cards_for_deck(deck_id):
    """
    Return all cards for a deck as a list of dicts with keys:
    id, deck_id, question, answer.

    Args:
        deck_id (int): The deck whose cards you want.

    Returns:
        list[dict]
    """
    with _get_conn() as conn:
        rows = conn.execute(
            "SELECT id, deck_id, question, answer FROM cards WHERE deck_id = ?",
            (deck_id,)
        ).fetchall()
    return [dict(r) for r in rows]


def get_card(card_id):
    """
    Return a single card dict (id, deck_id, question, answer) or None.
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT id, deck_id, question, answer FROM cards WHERE id = ?",
            (card_id,)
        ).fetchone()
    return dict(row) if row else None


def add_card(deck_id, question, answer):
    """
    Add a new flashcard to a deck and return its new id.

    Args:
        deck_id (int):  The deck this card belongs to.
        question (str): The question text.
        answer (str):   The answer text.

    Returns:
        int: The id of the newly created card.
    """
    with _get_conn() as conn:
        cursor = conn.execute(
            "INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
            (deck_id, question, answer)
        )
        return cursor.lastrowid


def update_card(card_id, question=None, answer=None):
    """
    Update the question and/or answer of an existing card.

    Args:
        card_id (int):  The card to update.
        question (str): New question text (optional).
        answer (str):   New answer text (optional).
    """
    fields, values = [], []
    if question is not None:
        fields.append("question = ?")
        values.append(question)
    if answer is not None:
        fields.append("answer = ?")
        values.append(answer)
    if not fields:
        return
    values.append(card_id)
    with _get_conn() as conn:
        conn.execute(
            f"UPDATE cards SET {', '.join(fields)} WHERE id = ?", values
        )


def delete_card(card_id):
    """
    Delete a single flashcard.

    Args:
        card_id (int): The card to remove.
    """
    with _get_conn() as conn:
        conn.execute("DELETE FROM cards WHERE id = ?", (card_id,))


# ── Quiz result functions ────────────────────────────────────────────────────

def save_quiz_result(deck_id, total_cards, correct, incorrect):
    """
    Record the result of a completed quiz session.

    Args:
        deck_id (int):     The deck that was quizzed.
        total_cards (int): Total number of cards attempted.
        correct (int):     Number answered correctly.
        incorrect (int):   Number answered incorrectly.

    Returns:
        int: The id of the newly saved result row.
    """
    with _get_conn() as conn:
        cursor = conn.execute(
            """INSERT INTO quiz_results (deck_id, total_cards, correct, incorrect)
               VALUES (?, ?, ?, ?)""",
            (deck_id, total_cards, correct, incorrect)
        )
        return cursor.lastrowid


def get_quiz_history(deck_id=None):
    """
    Return past quiz results as a list of dicts with keys:
    id, deck_id, total_cards, correct, incorrect, timestamp.

    Args:
        deck_id (int | None): Filter by deck. Pass None to get ALL results.

    Returns:
        list[dict]: Most recent results first.
    """
    with _get_conn() as conn:
        if deck_id is None:
            rows = conn.execute(
                "SELECT * FROM quiz_results ORDER BY timestamp DESC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM quiz_results WHERE deck_id = ? ORDER BY timestamp DESC",
                (deck_id,)
            ).fetchall()
    return [dict(r) for r in rows]


def get_best_score(deck_id):
    """
    Return the highest correct count ever achieved for a deck, or 0.

    Args:
        deck_id (int): The deck to look up.

    Returns:
        int: Maximum correct answers in a single quiz session.
    """
    with _get_conn() as conn:
        row = conn.execute(
            "SELECT MAX(correct) FROM quiz_results WHERE deck_id = ?",
            (deck_id,)
        ).fetchone()
    return row[0] if row and row[0] is not None else 0


# ── Seed helper (development / testing only) ────────────────────────────────

def seed_sample_data():
    """
    Populate the database with sample decks and cards for testing.
    Safe to call multiple times -- skips insertion if decks already exist.
    Remove or disable this once real user data flows in.
    """
    if get_all_decks():
        return  # already seeded

    sample = {
        ("Python Basics", "Computer Science"): [
            ("What keyword starts a function definition?", "def"),
            ("What data type stores key-value pairs?", "Dictionary (dict)"),
            ("What does len() return?", "The number of items in an object"),
            ("What is the result of 5 // 2?", "2 (floor division)"),
            ("How do you open a file safely in Python?",
             "Using a 'with' statement: with open(filename) as f"),
        ],
        ("World Capitals", "Geography"): [
            ("What is the capital of Japan?", "Tokyo"),
            ("What is the capital of Brazil?", "Brasilia"),
            ("What is the capital of Australia?", "Canberra"),
            ("What is the capital of Canada?", "Ottawa"),
            ("What is the capital of South Africa?",
             "Pretoria (executive), Cape Town (legislative), Bloemfontein (judicial)"),
        ],
    }

    for (deck_name, subject), cards in sample.items():
        deck_id = add_deck(deck_name, subject)
        for question, answer in cards:
            add_card(deck_id, question, answer)
