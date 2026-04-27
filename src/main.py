"""
main.py
StudyGeeks -- Flashcard Learning Application
CS-122 | Spring 2026

Main entry point that ties together all modules:
  - Create and manage flashcard decks
  - Quiz mode (study with self-grading)
  - View progress and stats

Run:  python main.py
"""

import os
import db
import quiz_mode
import deck_manager


# ─────────────────────────────────────────────
# CLI HELPERS
# ─────────────────────────────────────────────

def clear():
    os.system("cls" if os.name == "nt" else "clear")


def divider(char="─", width=50):
    print(char * width)


def prompt_enter(message="Press Enter to continue..."):
    input(f"\n  {message}")


# ─────────────────────────────────────────────
# MAIN MENU
# ─────────────────────────────────────────────

def show_menu():
    clear()
    print("\n")
    divider("═")
    print("  StudyGeeks -- Flashcard Learning App")
    divider("═")
    print()
    print("  1.  Create a New Deck")
    print("  2.  View & Manage Decks")
    print("  3.  Quiz Mode")
    print("  4.  View Progress")
    print("  5.  Quit")
    print()
    divider("═")
    print()


def view_progress():
    """Show quiz history and best scores for each deck."""
    clear()
    print("\n")
    divider("═")
    print("  Your Study Progress")
    divider("═")

    decks = db.get_all_decks()

    if not decks:
        print("\n  No decks yet. Create one to get started!")
        prompt_enter()
        return

    has_history = False

    for deck in decks:
        history = db.get_quiz_history(deck["id"])
        if not history:
            continue

        has_history = True
        best = db.get_best_score(deck["id"])
        total_cards = history[0]["total_cards"]  # from most recent quiz
        attempts = len(history)

        # calculate average score across all attempts
        total_correct = sum(h["correct"] for h in history)
        total_attempted = sum(h["total_cards"] for h in history)
        avg_pct = round((total_correct / total_attempted) * 100) if total_attempted > 0 else 0

        print(f"\n  {deck['name']}")
        divider("─", 40)
        print(f"     Attempts:     {attempts}")
        print(f"     Best Score:   {best}/{total_cards}")
        print(f"     Avg Accuracy: {avg_pct}%")
        print(f"     Last Played:  {history[0]['timestamp']}")

    if not has_history:
        print("\n  No quiz results yet. Take a quiz to see your stats!")

    print()
    divider("═")
    prompt_enter()


# ─────────────────────────────────────────────
# APP LOOP
# ─────────────────────────────────────────────

def main():
    # set up database tables and load sample data
    db.init()
    db.seed_sample_data()

    while True:
        show_menu()
        choice = input("  Enter your choice (1-5): ").strip()

        if choice == "1":
            deck_manager.create_deck_flow()

        elif choice == "2":
            deck_manager.manage_decks_flow()

        elif choice == "3":
            quiz_mode.main()

        elif choice == "4":
            view_progress()

        elif choice == "5":
            clear()
            print("\n")
            divider("═")
            print("  Thanks for studying with StudyGeeks!")
            print("  Remember: repetition is how it sticks.")
            divider("═")
            print()
            break

        else:
            print("\n  Invalid choice. Please enter 1-5.")
            prompt_enter()


if __name__ == "__main__":
    main()