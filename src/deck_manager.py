"""
deck_manager.py
StudyGeeks -- Deck Creation & Management
CS-122 | Spring 2026

Handles:
  - Creating new decks with flashcards
  - Viewing all decks and their cards
  - Editing existing cards
  - Deleting decks or individual cards
  - Adding cards to existing decks
"""

import os
import db


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
# CREATE DECK
# ─────────────────────────────────────────────

def create_deck_flow():
    """Walk the user through creating a new deck with cards."""
    clear()
    print("\n")
    divider("═")
    print("  Create a New Deck")
    divider("═")

    name = input("\n  Deck name: ").strip()
    if not name:
        print("  Deck name cannot be empty.")
        prompt_enter()
        return

    subject = input("  Subject (optional, press Enter to skip): ").strip()
    subject = subject if subject else None

    deck_id = db.add_deck(name, subject)
    print(f"\n  Deck '{name}' created!")
    divider()

    print("\n  Now add some flashcards.")
    print("  Type 'done' as the question when you're finished.\n")

    count = 0
    while True:
        print(f"  --- Card {count + 1} ---")
        question = input("  Question: ").strip()

        if question.lower() == "done":
            break

        if not question:
            print("  Question cannot be empty. Try again.\n")
            continue

        answer = input("  Answer:   ").strip()

        if not answer:
            print("  Answer cannot be empty. Try again.\n")
            continue

        db.add_card(deck_id, question, answer)
        count += 1
        print(f"  Card added!\n")

    print()
    divider("═")
    if count == 0:
        print(f"  Deck '{name}' created with no cards.")
        print("  You can add cards later from Manage Decks.")
    else:
        print(f"  Deck '{name}' created with {count} card{'s' if count != 1 else ''}.")
    divider("═")
    prompt_enter()


# ─────────────────────────────────────────────
# MANAGE DECKS
# ─────────────────────────────────────────────

def manage_decks_flow():
    """View all decks and choose one to manage."""
    while True:
        clear()
        print("\n")
        divider("═")
        print("  Your Decks")
        divider("═")

        decks = db.get_all_decks()

        if not decks:
            print("\n  No decks yet. Create one first!")
            prompt_enter()
            return

        for i, deck in enumerate(decks, start=1):
            cards = db.get_cards_for_deck(deck["id"])
            subject_label = f" ({deck['subject']})" if deck.get("subject") else ""
            print(f"  {i}. {deck['name']}{subject_label}  [{len(cards)} cards]")

        print()
        divider()
        print("  B. Back to main menu\n")

        choice = input("  Pick a deck number to manage: ").strip().upper()

        if choice == "B":
            return

        if choice.isdigit() and 1 <= int(choice) <= len(decks):
            selected = decks[int(choice) - 1]
            deck_detail(selected["id"])
        else:
            print("  Invalid choice.")
            prompt_enter()


def deck_detail(deck_id):
    """Show a single deck's cards and management options."""
    while True:
        clear()
        deck = db.get_deck(deck_id)

        if not deck:
            print("  Deck not found.")
            prompt_enter()
            return

        cards = db.get_cards_for_deck(deck_id)

        print("\n")
        divider("═")
        subject_label = f" ({deck['subject']})" if deck.get("subject") else ""
        print(f"  {deck['name']}{subject_label}")
        divider("═")

        if cards:
            for i, card in enumerate(cards, start=1):
                print(f"\n  Card {i}:")
                print(f"    Q: {card['question']}")
                print(f"    A: {card['answer']}")
            print()
            divider()
        else:
            print("\n  This deck has no cards yet.\n")
            divider()

        print()
        print("  1.  Add cards")
        print("  2.  Edit a card")
        print("  3.  Delete a card")
        print("  4.  Delete this entire deck")
        print("  5.  Back to deck list")
        print()

        action = input("  Choose an action (1-5): ").strip()

        if action == "1":
            add_cards_to_deck(deck_id, deck["name"])
        elif action == "2":
            edit_card_flow(deck_id)
        elif action == "3":
            delete_card_flow(deck_id)
        elif action == "4":
            confirm = input(f"\n  Delete '{deck['name']}' and all its cards? (yes/no): ").strip().lower()
            if confirm == "yes":
                db.delete_deck(deck_id)
                print(f"\n  Deck '{deck['name']}' deleted.")
                prompt_enter()
                return
            else:
                print("  Cancelled.")
                prompt_enter()
        elif action == "5":
            return
        else:
            print("  Invalid choice.")
            prompt_enter()


# ─────────────────────────────────────────────
# ADD / EDIT / DELETE CARDS
# ─────────────────────────────────────────────

def add_cards_to_deck(deck_id, deck_name):
    """Add more cards to an existing deck."""
    print(f"\n  Adding cards to '{deck_name}'.")
    print("  Type 'done' as the question when you're finished.\n")

    count = 0
    while True:
        question = input("  Question: ").strip()

        if question.lower() == "done":
            break
        if not question:
            print("  Question cannot be empty.\n")
            continue

        answer = input("  Answer:   ").strip()
        if not answer:
            print("  Answer cannot be empty.\n")
            continue

        db.add_card(deck_id, question, answer)
        count += 1
        print(f"  Card added!\n")

    print(f"\n  {count} card{'s' if count != 1 else ''} added.")
    prompt_enter()


def edit_card_flow(deck_id):
    """Let user pick a card to edit."""
    cards = db.get_cards_for_deck(deck_id)

    if not cards:
        print("\n  No cards to edit.")
        prompt_enter()
        return

    print("\n  Which card do you want to edit?")
    for i, card in enumerate(cards, start=1):
        print(f"  {i}. {card['question']}")

    choice = input("\n  Card number: ").strip()

    if not choice.isdigit() or not (1 <= int(choice) <= len(cards)):
        print("  Invalid choice.")
        prompt_enter()
        return

    card = cards[int(choice) - 1]
    print(f"\n  Current question: {card['question']}")
    new_q = input("  New question (Enter to keep current): ").strip()

    print(f"  Current answer: {card['answer']}")
    new_a = input("  New answer (Enter to keep current): ").strip()

    db.update_card(
        card["id"],
        question=new_q if new_q else None,
        answer=new_a if new_a else None
    )
    print("\n  Card updated!")
    prompt_enter()


def delete_card_flow(deck_id):
    """Let user pick a card to delete."""
    cards = db.get_cards_for_deck(deck_id)

    if not cards:
        print("\n  No cards to delete.")
        prompt_enter()
        return

    print("\n  Which card do you want to delete?")
    for i, card in enumerate(cards, start=1):
        print(f"  {i}. {card['question']}")

    choice = input("\n  Card number: ").strip()

    if not choice.isdigit() or not (1 <= int(choice) <= len(cards)):
        print("  Invalid choice.")
        prompt_enter()
        return

    card = cards[int(choice) - 1]
    confirm = input(f"  Delete '{card['question']}'? (yes/no): ").strip().lower()

    if confirm == "yes":
        db.delete_card(card["id"])
        print("  Card deleted!")
    else:
        print("  Cancelled.")

    prompt_enter()