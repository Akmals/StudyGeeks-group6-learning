/* ═══════════════════════════════════════════════════════════════════════════
   StudyGeeks — app.js
   Single-page application logic: routing, API calls, study mode, UI helpers
   ═══════════════════════════════════════════════════════════════════════════ */

// ── State ───────────────────────────────────────────────────────────────────

const state = {
  currentDeckId:   null,
  currentDeckName: '',
  cards:           [],
  studyCards:      [],
  studyIndex:      0,
  isFlipped:       false,
  correct:         0,
  incorrect:       0,
};


// ── API Client ──────────────────────────────────────────────────────────────

const api = {
  async getDecks() {
    const res = await fetch('/api/decks');
    return res.json();
  },

  async createDeck(name, subject) {
    const res = await fetch('/api/decks', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, subject }),
    });
    return res.json();
  },

  async deleteDeck(id) {
    await fetch(`/api/decks/${id}`, { method: 'DELETE' });
  },

  async getCards(deckId) {
    const res = await fetch(`/api/decks/${deckId}/cards`);
    return res.json();
  },

  async addCard(deckId, question, answer) {
    const res = await fetch(`/api/decks/${deckId}/cards`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer }),
    });
    return res.json();
  },

  async updateCard(cardId, question, answer) {
    await fetch(`/api/cards/${cardId}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, answer }),
    });
  },

  async deleteCard(cardId) {
    await fetch(`/api/cards/${cardId}`, { method: 'DELETE' });
  },

  async saveQuizResult(deckId, totalCards, correct, incorrect) {
    await fetch(`/api/decks/${deckId}/quiz-result`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ total_cards: totalCards, correct, incorrect }),
    });
  },
};


// ── Router ──────────────────────────────────────────────────────────────────

const router = {
  go(view, data) {
    // hide all views
    document.querySelectorAll('.view').forEach(v => v.classList.remove('active'));

    switch (view) {
      case 'dashboard':
        document.getElementById('view-dashboard').classList.add('active');
        this.loadDashboard();
        break;

      case 'deck':
        document.getElementById('view-deck').classList.add('active');
        this.loadDeck(data);
        break;

      case 'study':
        document.getElementById('view-study').classList.add('active');
        break;

      case 'results':
        document.getElementById('view-results').classList.add('active');
        break;
    }

    window.scrollTo({ top: 0, behavior: 'smooth' });
  },

  async loadDashboard() {
    const decks = await api.getDecks();
    const grid  = document.getElementById('deck-grid');
    const empty = document.getElementById('empty-state');

    if (decks.length === 0) {
      grid.innerHTML = '';
      empty.classList.remove('hidden');
      return;
    }

    empty.classList.add('hidden');
    grid.innerHTML = decks.map(d => `
      <div class="deck-card" onclick="router.go('deck', ${d.id})">
        <div class="deck-card-subject">${d.subject || 'General'}</div>
        <div class="deck-card-name">${escapeHtml(d.name)}</div>
        <div class="deck-card-count"><strong>${d.card_count}</strong> card${d.card_count !== 1 ? 's' : ''}</div>
      </div>
    `).join('');
  },

  async loadDeck(deckId) {
    state.currentDeckId = deckId;
    const decks = await api.getDecks();
    const deck  = decks.find(d => d.id === deckId);
    if (!deck) return router.go('dashboard');

    state.currentDeckName = deck.name;

    document.getElementById('deck-title').textContent = deck.name;
    document.getElementById('deck-subject').textContent = deck.subject || 'General';

    await this.refreshCards();
  },

  async refreshCards() {
    const cards    = await api.getCards(state.currentDeckId);
    state.cards    = cards;
    const list     = document.getElementById('card-list');
    const empty    = document.getElementById('cards-empty');
    const studyBtn = document.getElementById('btn-study');

    if (cards.length === 0) {
      list.innerHTML = '';
      empty.classList.remove('hidden');
      studyBtn.disabled = true;
      studyBtn.style.opacity = '0.4';
      return;
    }

    empty.classList.add('hidden');
    studyBtn.disabled = false;
    studyBtn.style.opacity = '1';

    list.innerHTML = cards.map((c, i) => `
      <div class="card-item">
        <div class="card-item-content">
          <div class="card-item-q">${escapeHtml(c.question)}</div>
          <div class="card-item-a">${escapeHtml(c.answer)}</div>
        </div>
        <div class="card-item-actions">
          <button title="Edit" onclick="ui.openEditModal(${c.id}, ${i})">Edit</button>
          <button title="Delete" class="btn-del" onclick="ui.deleteCard(${c.id})">Del</button>
        </div>
      </div>
    `).join('');
  },
};


// ── UI Helpers ──────────────────────────────────────────────────────────────

const ui = {
  // — New Deck Modal —
  showNewDeckModal() {
    document.getElementById('modal-deck-name').value = '';
    document.getElementById('modal-deck-subject').value = '';
    document.getElementById('modal-overlay').classList.remove('hidden');
    document.getElementById('modal-deck-name').focus();
  },

  closeModal() {
    document.getElementById('modal-overlay').classList.add('hidden');
  },

  async createDeck() {
    const name    = document.getElementById('modal-deck-name').value.trim();
    const subject = document.getElementById('modal-deck-subject').value.trim();
    if (!name) { toast('Please enter a deck name'); return; }
    await api.createDeck(name, subject);
    this.closeModal();
    toast('Deck created!');
    router.go('dashboard');
  },

  // — Delete Deck —
  async confirmDeleteDeck() {
    if (!confirm(`Delete "${state.currentDeckName}" and all its cards?`)) return;
    await api.deleteDeck(state.currentDeckId);
    toast('Deck deleted');
    router.go('dashboard');
  },

  // — Add Card —
  async addCard() {
    const q = document.getElementById('input-question').value.trim();
    const a = document.getElementById('input-answer').value.trim();
    if (!q || !a) { toast('Please fill in both fields'); return; }
    await api.addCard(state.currentDeckId, q, a);
    document.getElementById('input-question').value = '';
    document.getElementById('input-answer').value = '';
    toast('Card added');
    router.refreshCards();
  },

  // — Edit Card Modal —
  _editingCardId: null,

  openEditModal(cardId, index) {
    const card = state.cards[index];
    this._editingCardId = cardId;
    document.getElementById('edit-question').value = card.question;
    document.getElementById('edit-answer').value   = card.answer;
    document.getElementById('edit-modal-overlay').classList.remove('hidden');
    document.getElementById('edit-question').focus();
  },

  closeEditModal() {
    document.getElementById('edit-modal-overlay').classList.add('hidden');
    this._editingCardId = null;
  },

  async saveEditCard() {
    const q = document.getElementById('edit-question').value.trim();
    const a = document.getElementById('edit-answer').value.trim();
    if (!q || !a) { toast('Both fields are required'); return; }
    await api.updateCard(this._editingCardId, q, a);
    this.closeEditModal();
    toast('Card updated');
    router.refreshCards();
  },

  // — Delete Card —
  async deleteCard(cardId) {
    if (!confirm('Delete this card?')) return;
    await api.deleteCard(cardId);
    toast('Card deleted');
    router.refreshCards();
  },
};


// ── Study Mode ──────────────────────────────────────────────────────────────

const study = {
  start() {
    if (state.cards.length === 0) { toast('Add some cards first!'); return; }

    // Shuffle
    state.studyCards = [...state.cards].sort(() => Math.random() - 0.5);
    state.studyIndex = 0;
    state.correct    = 0;
    state.incorrect  = 0;
    state.isFlipped  = false;

    router.go('study');
    this.showCard();
  },

  showCard() {
    const card  = state.studyCards[state.studyIndex];
    const total = state.studyCards.length;
    const idx   = state.studyIndex + 1;

    // Reset flip
    state.isFlipped = false;
    document.getElementById('study-card').classList.remove('flipped');

    // Fill content
    document.getElementById('study-question').textContent = card.question;
    document.getElementById('study-answer').textContent   = card.answer;
    document.getElementById('study-counter').textContent   = `Card ${idx} of ${total}`;

    // Progress bar
    const pct = ((idx - 1) / total) * 100;
    document.getElementById('study-progress-bar').style.width = pct + '%';

    // Show flip hint, hide grade buttons
    document.getElementById('study-flip-hint').classList.remove('hidden');
    document.getElementById('study-grade-btns').classList.add('hidden');
  },

  flip() {
    state.isFlipped = !state.isFlipped;
    document.getElementById('study-card').classList.toggle('flipped');
    if (state.isFlipped) {
      document.getElementById('study-flip-hint').classList.add('hidden');
      document.getElementById('study-grade-btns').classList.remove('hidden');
    } else {
      document.getElementById('study-flip-hint').classList.remove('hidden');
      document.getElementById('study-grade-btns').classList.add('hidden');
    }
  },

  grade(knew) {
    if (knew) {
      state.correct++;
    } else {
      state.incorrect++;
    }

    state.studyIndex++;

    if (state.studyIndex >= state.studyCards.length) {
      this.finish();
    } else {
      this.showCard();
    }
  },

  async finish() {
    const total   = state.studyCards.length;
    const correct = state.correct;
    const wrong   = state.incorrect;
    const pct     = Math.round((correct / total) * 100);

    // Save result
    await api.saveQuizResult(state.currentDeckId, total, correct, wrong);

    // Fill results view
    document.getElementById('results-deck-name').textContent = state.currentDeckName;
    document.getElementById('res-correct').textContent   = correct;
    document.getElementById('res-incorrect').textContent  = wrong;
    document.getElementById('res-total').textContent      = total;
    document.getElementById('score-pct').textContent      = pct + '%';

    // Progress ring animation
    const circumference = 2 * Math.PI * 52; // r = 52
    const offset = circumference - (pct / 100) * circumference;
    const ring = document.getElementById('score-ring-fill');
    ring.style.strokeDasharray  = circumference;
    ring.style.strokeDashoffset = circumference;
    // Force reflow then animate
    ring.getBoundingClientRect();
    setTimeout(() => { ring.style.strokeDashoffset = offset; }, 50);

    // Message
    let msg = '';
    if (pct === 100)     msg = 'Perfect score! You\'ve mastered this deck.';
    else if (pct >= 80)  msg = 'Great job! Almost there!';
    else if (pct >= 50)  msg = 'Good progress -- keep reviewing!';
    else                 msg = 'Keep going -- repetition is key!';
    document.getElementById('results-message').textContent = msg;

    // Progress bar full
    document.getElementById('study-progress-bar').style.width = '100%';

    router.go('results');
  },

  quit() {
    router.go('deck', state.currentDeckId);
  },
};


// ── Keyboard Support ────────────────────────────────────────────────────────

document.addEventListener('keydown', (e) => {
  // Only when study view is active
  if (!document.getElementById('view-study').classList.contains('active')) return;

  if (e.code === 'Space' || e.code === 'Enter') {
    e.preventDefault();
    study.flip();
  } else if (e.key === '1' && state.isFlipped) {
    study.grade(true);
  } else if (e.key === '2' && state.isFlipped) {
    study.grade(false);
  }
});


// ── Toast Notification ──────────────────────────────────────────────────────

let toastTimer = null;
function toast(msg) {
  const el = document.getElementById('toast');
  el.textContent = msg;
  el.classList.remove('hidden');
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    el.classList.remove('show');
    setTimeout(() => el.classList.add('hidden'), 300);
  }, 2200);
}


// ── Escape HTML ─────────────────────────────────────────────────────────────

function escapeHtml(str) {
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}


// ── SVG Gradient for Score Ring ──────────────────────────────────────────────

function injectSvgDefs() {
  const svg = document.querySelector('.score-ring');
  if (!svg) return;
  const defs = document.createElementNS('http://www.w3.org/2000/svg', 'defs');
  defs.innerHTML = `
    <linearGradient id="ring-grad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%"   stop-color="#7c5cfc" />
      <stop offset="100%" stop-color="#22d3ee" />
    </linearGradient>
  `;
  svg.prepend(defs);
}


// ── Init ────────────────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  injectSvgDefs();
  router.go('dashboard');
});
