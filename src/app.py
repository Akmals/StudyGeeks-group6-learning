"""
app.py
StudyGeeks -- Flask Web Server
Author: Akmal (UI Layer)

Serves the single-page web interface and exposes a JSON API
that delegates to db.py for all data operations.

Run:
    python src/app.py
    Open http://localhost:5000
"""

from flask import Flask, jsonify, request, send_from_directory
import os
import db

# ── Flask setup ──────────────────────────────────────────────────────────────

_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_STATIC_DIR = os.path.join(_SRC_DIR, "static")

app = Flask(__name__, static_folder=_STATIC_DIR)


# ── Static file routes ──────────────────────────────────────────────────────

@app.route("/")
def index():
    return send_from_directory(_STATIC_DIR, "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(_STATIC_DIR, filename)


# ── Deck API ────────────────────────────────────────────────────────────────

@app.route("/api/decks", methods=["GET"])
def api_get_decks():
    """Return all decks with their card counts."""
    decks = db.get_all_decks()
    for deck in decks:
        cards = db.get_cards_for_deck(deck["id"])
        deck["card_count"] = len(cards)
    return jsonify(decks)


@app.route("/api/decks", methods=["POST"])
def api_create_deck():
    """Create a new deck. Body: { name, subject }"""
    data = request.get_json(force=True)
    name = data.get("name", "").strip()
    subject = data.get("subject", "").strip() or None
    if not name:
        return jsonify({"error": "Deck name is required"}), 400
    deck_id = db.add_deck(name, subject)
    return jsonify({"id": deck_id, "name": name, "subject": subject}), 201


@app.route("/api/decks/<int:deck_id>", methods=["DELETE"])
def api_delete_deck(deck_id):
    """Delete a deck and all its cards."""
    db.delete_deck(deck_id)
    return jsonify({"ok": True})


# ── Card API ────────────────────────────────────────────────────────────────

@app.route("/api/decks/<int:deck_id>/cards", methods=["GET"])
def api_get_cards(deck_id):
    """Return all cards for a deck."""
    cards = db.get_cards_for_deck(deck_id)
    return jsonify(cards)


@app.route("/api/decks/<int:deck_id>/cards", methods=["POST"])
def api_add_card(deck_id):
    """Add a card. Body: { question, answer }"""
    data = request.get_json(force=True)
    question = data.get("question", "").strip()
    answer = data.get("answer", "").strip()
    if not question or not answer:
        return jsonify({"error": "Both question and answer are required"}), 400
    card_id = db.add_card(deck_id, question, answer)
    return jsonify({"id": card_id, "deck_id": deck_id,
                    "question": question, "answer": answer}), 201


@app.route("/api/cards/<int:card_id>", methods=["PUT"])
def api_update_card(card_id):
    """Edit a card. Body: { question, answer }"""
    data = request.get_json(force=True)
    db.update_card(card_id,
                   question=data.get("question"),
                   answer=data.get("answer"))
    return jsonify({"ok": True})


@app.route("/api/cards/<int:card_id>", methods=["DELETE"])
def api_delete_card(card_id):
    """Delete a single card."""
    db.delete_card(card_id)
    return jsonify({"ok": True})


# ── Quiz Result API ─────────────────────────────────────────────────────────

@app.route("/api/decks/<int:deck_id>/quiz-result", methods=["POST"])
def api_save_quiz_result(deck_id):
    """Save quiz results. Body: { total_cards, correct, incorrect }"""
    data = request.get_json(force=True)
    result_id = db.save_quiz_result(
        deck_id,
        data["total_cards"],
        data["correct"],
        data["incorrect"],
    )
    return jsonify({"id": result_id}), 201


@app.route("/api/decks/<int:deck_id>/quiz-history", methods=["GET"])
def api_get_quiz_history(deck_id):
    """Return quiz history for a deck."""
    history = db.get_quiz_history(deck_id)
    return jsonify(history)


# ── Start ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    db.init()
    db.seed_sample_data()
    print("\n  StudyGeeks is running at http://localhost:5000\n")
    app.run(debug=True, port=5000)
