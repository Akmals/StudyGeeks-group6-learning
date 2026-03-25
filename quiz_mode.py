"""
quiz_mode.py
Flashcard Learning Application -- Quiz Mode
Author: Shivangi
Sprint 2

Supports:
  - Flashcard flip (show question, reveal answer on Enter)
  - Self-grading (Know it / Still learning)
  - Score summary with results stored in SQLite

Database note:
  This module uses a local SQLite file (flashcards.db).
  Mock data is seeded on first run so the app works standalone.
  When Akmal's schema is finalized, replace the seed_mock_data()
  call and table definitions with the real schema -- the quiz logic
  stays the same.
"""

import sqlite3
import random
import os

DB_PATH = "flashcards.db"


# ─────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────

def get_connection():
    """Return a connection to the SQLite database."""
    return sqlite3.connect(DB_PATH)


def setup_tables():
    """
    Create tables if they don't exist.
    NOTE FOR AKMAL/DEVIN: Replace these CREATE statements with the
    finalized schema. Keep column names consistent so quiz_mode.py
    doesn't need changes.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS decks (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            subject TEXT
        );

        CREATE TABLE IF NOT EXISTS cards (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id    INTEGER NOT NULL,
            question   TEXT NOT NULL,
            answer     TEXT NOT NULL,
            FOREIGN KEY (deck_id) REFERENCES decks(id)
        );

        CREATE TABLE IF NOT EXISTS quiz_results (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            deck_id      INTEGER NOT NULL,
            total_cards  INTEGER NOT NULL,
            correct      INTEGER NOT NULL,
            incorrect    INTEGER NOT NULL,
            timestamp    DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (deck_id) REFERENCES decks(id)
        );
    """)

    conn.commit()
    conn.close()


def seed_mock_data():
    """
    Insert sample decks and cards for testing.
    Only runs if the decks table is empty.
    Remove or replace this once real user data is flowing in.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM decks")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return  # already seeded

    mock_decks = [
        ("Python Basics", "Computer Science"),
        ("World Capitals", "Geography"),
    ]

    mock_cards = {
        "Python Basics": [
            ("What keyword starts a function definition?", "def"),
            ("What data type stores key-value pairs?", "Dictionary (dict)"),
            ("What does len() return?", "The number of items in an object"),
            ("What is the result of 5 // 2?", "2 (floor division)"),
            ("How do you open a file safely in Python?", "Using a 'with' statement: with open(filename) as f"),
        ],
        "World Capitals": [
            ("What is the capital of Japan?", "Tokyo"),
            ("What is the capital of Brazil?", "Brasilia"),
            ("What is the capital of Australia?", "Canberra"),
            ("What is the capital of Canada?", "Ottawa"),
            ("What is the capital of South Africa?", "Pretoria (executive), Cape Town (legislative), Bloemfontein (judicial)"),
        ],
    }

    for deck_name, subject in mock_decks:
        cursor.execute(
            "INSERT INTO decks (name, subject) VALUES (?, ?)",
            (deck_name, subject)
        )
        deck_id = cursor.lastrowid
        for question, answer in mock_cards[deck_name]:
            cursor.execute(
                "INSERT INTO cards (deck_id, question, answer) VALUES (?, ?, ?)",
                (deck_id, question, answer)
            )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# DATA FETCHERS
# ─────────────────────────────────────────────

def get_all_decks():
    """Return list of (id, name, subject) for all decks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, subject FROM decks ORDER BY name")
    decks = cursor.fetchall()
    conn.close()
    return decks


def get_cards_for_deck(deck_id):
    """Return list of (id, question, answer) for a given deck."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, question, answer FROM cards WHERE deck_id = ?",
        (deck_id,)
    )
    cards = cursor.fetchall()
    conn.close()
    return cards


def save_quiz_result(deck_id, total, correct, incorrect):
    """Persist the quiz result to the quiz_results table."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO quiz_results (deck_id, total_cards, correct, incorrect)
           VALUES (?, ?, ?, ?)""",
        (deck_id, total, correct, incorrect)
    )
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────
# CLI HELPERS
# ─────────────────────────────────────────────

def clear():
    """Clear the terminal screen."""
    os.system("cls" if os.name == "nt" else "clear")


def divider(char="─", width=50):
    print(char * width)


def prompt_enter(message="Press Enter to continue..."):
    input(f"\n  {message}")


# ─────────────────────────────────────────────
# QUIZ FLOW
# ─────────────────────────────────────────────

def pick_deck(decks):
    """
    Show available decks and return the chosen (deck_id, deck_name).
    Returns None if user quits.
    """
    print("\n  📚  Available Decks\n")
    divider()
    for i, (deck_id, name, subject) in enumerate(decks, start=1):
        subject_label = f"({subject})" if subject else ""
        print(f"  {i}. {name} {subject_label}")
    divider()
    print("  Q. Quit\n")

    while True:
        choice = input("  Enter deck number: ").strip().upper()
        if choice == "Q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(decks):
            selected = decks[int(choice) - 1]
            return selected[0], selected[1]  # deck_id, name
        print("  Invalid choice. Try again.")


def run_quiz(deck_id, deck_name, cards):
    """
    Core quiz loop.
    Returns (correct_count, incorrect_count).
    """
    random.shuffle(cards)
    correct = 0
    incorrect = 0
    total = len(cards)

    for i, (card_id, question, answer) in enumerate(cards, start=1):
        clear()
        print(f"\n  🃏  {deck_name}  |  Card {i} of {total}\n")
        divider()
        print(f"\n  Q: {question}\n")
        divider()

        input("  Press Enter to reveal the answer...")

        clear()
        print(f"\n  🃏  {deck_name}  |  Card {i} of {total}\n")
        divider()
        print(f"\n  Q: {question}\n")
        divider()
        print(f"\n  A: {answer}\n")
        divider()

        print("\n  Did you get it right?")
        print("  1. Yes, I knew it  ✓")
        print("  2. Not quite, still learning  ✗\n")

        while True:
            grade = input("  Enter 1 or 2: ").strip()
            if grade == "1":
                correct += 1
                print("\n  Nice work! Moving on...")
                break
            elif grade == "2":
                incorrect += 1
                print("\n  No worries, keep going!")
                break
            else:
                print("  Please enter 1 or 2.")

        prompt_enter()

    return correct, incorrect


def show_summary(deck_name, total, correct, incorrect):
    """Display end-of-quiz score summary."""
    clear()
    pct = round((correct / total) * 100) if total > 0 else 0

    print("\n")
    divider("═")
    print(f"  📊  Quiz Complete: {deck_name}")
    divider("═")
    print(f"\n  Total Cards:      {total}")
    print(f"  Knew It:          {correct}  ✓")
    print(f"  Still Learning:   {incorrect}  ✗")
    print(f"  Score:            {pct}%")
    divider()

    if pct == 100:
        print("\n  Perfect score! You've mastered this deck. 🏆")
    elif pct >= 70:
        print("\n  Great job! A little more review and you'll have it. 💪")
    else:
        print("\n  Keep going -- repetition is how it sticks. 📖")

    print()
    divider("═")
    print()


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():
    setup_tables()
    seed_mock_data()

    clear()
    print("\n")
    divider("═")
    print("  🎴  Flashcard Learning App -- Quiz Mode")
    divider("═")

    while True:
        decks = get_all_decks()

        if not decks:
            print("\n  No decks found. Add some cards first!")
            break

        result = pick_deck(decks)
        if result is None:
            print("\n  Goodbye! Keep studying. 👋\n")
            break

        deck_id, deck_name = result
        cards = get_cards_for_deck(deck_id)

        if not cards:
            print(f"\n  The deck '{deck_name}' has no cards yet.")
            prompt_enter()
            continue

        correct, incorrect = run_quiz(deck_id, deck_name, cards)
        total = correct + incorrect

        save_quiz_result(deck_id, total, correct, incorrect)
        show_summary(deck_name, total, correct, incorrect)

        print("  1. Quiz another deck")
        print("  2. Quit\n")

        again = input("  Enter 1 or 2: ").strip()
        if again != "1":
            print("\n  Goodbye! Keep studying. 👋\n")
            break


if __name__ == "__main__":
    main()
