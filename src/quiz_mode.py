"""
quiz_mode.py
Flashcard Learning Application -- Quiz Mode
Author: Shivangi
Sprint 2

Supports:
  - Flashcard flip (show question, reveal answer on Enter)
  - Self-grading (Know it / Still learning)
  - Score summary with results stored in SQLite

Database:
  All database work is handled by db.py.
  This module only contains quiz UI and flow logic.
"""

import random
import os

import db  # ← Akmal's database helper module


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
    decks is a list of dicts with keys: id, name, subject.
    Returns None if user quits.
    """
    print("\n  📚  Available Decks\n")
    divider()
    for i, deck in enumerate(decks, start=1):
        subject_label = f"({deck['subject']})" if deck.get("subject") else ""
        print(f"  {i}. {deck['name']} {subject_label}")
    divider()
    print("  Q. Quit\n")

    while True:
        choice = input("  Enter deck number: ").strip().upper()
        if choice == "Q":
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(decks):
            selected = decks[int(choice) - 1]
            return selected["id"], selected["name"]
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

    for i, card in enumerate(cards, start=1):
        card_id, question, answer = card["id"], card["question"], card["answer"]
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
    clear()
    print("\n")
    divider("═")
    print("  🎴  Flashcard Learning App -- Quiz Mode")
    divider("═")

    while True:
        decks = db.get_all_decks()

        if not decks:
            print("\n  No decks found. Add some cards first!")
            prompt_enter()
            break

        result = pick_deck(decks)
        if result is None:
            break

        deck_id, deck_name = result
        cards = db.get_cards_for_deck(deck_id)

        if not cards:
            print(f"\n  The deck '{deck_name}' has no cards yet.")
            prompt_enter()
            continue

        correct, incorrect = run_quiz(deck_id, deck_name, cards)
        total = correct + incorrect

        db.save_quiz_result(deck_id, total, correct, incorrect)
        show_summary(deck_name, total, correct, incorrect)

        print("  1. Quiz another deck")
        print("  2. Back to main menu\n")

        again = input("  Enter 1 or 2: ").strip()
        if again != "1":
            break


if __name__ == "__main__":
    main()