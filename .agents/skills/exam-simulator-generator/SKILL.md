---
name: exam-simulator-generator
description: >-
  Workflow and guidelines for building responsive, standalone, client-side
  interactive exam simulators (HTML/CSS/JS) for IELTS, SAT, and ESL.
  Supports dual-pane reading, instant grading, countdown timers, distractor
  breakdown toggles, and print/PDF views.
---

# 💻 Exam Simulator Generator Skill

Use this skill when creating or converting educational content into interactive web simulators.

---

## 🎨 UI & Design Principles

1. **Zero Server Dependencies**: Must run as self-contained HTML/CSS/JS (or clean modular assets) with **relative links only** — works via `file://`, and deploys unchanged on Vercel. Link every simulator to its domain hub (`../ESL/index.html`, `../IELTS/index.html`, `../SAT/index.html`), which in turn links to the master portal (`../index.html`).
2. **Dual-Pane Layout (for Reading & Data Prompts)**:
   - Left Pane: Passage, chart, or contextual stimulus with resizable splitter and text highlight capability.
   - Right Pane: Question cards, navigation pill bar, and instant feedback controls.
3. **Themes & Accessibility**:
   - Light & Dark mode support with persistent state via `localStorage`.
   - Accessible keyboard navigation (`1-4` or `A-D` for options, arrow keys for navigation).
   - Clean printable stylesheet (`@media print`) for converting modules directly to paper handouts or PDF.
4. **Pedagogical Features**:
   - Countdown timer with optional pause and retry modes.
   - Instant or exam-mode scoring (reveal immediately vs reveal on submit).
   - "Why is this right?" and "Why are distractors wrong?" accordion toggles for every question.
   - Question filter buttons (All, Answered, Unanswered, Bookmarked / Flagged).
5. **Student Tools Toolbar Standard** (SAT study pages; see `scripts/student_tools.py` + `scripts/add_student_tools.py`):
   - 🖊 Pen (draw on page, colors, eraser, per-page persistence), 🖍 Highlighter (selection-based, persists), 📝 Notes (autosaved panel), 🧮 Calculator (safe eval, `%`/`^`/`√`), 📖 Words (B1 glosses for hard words, tap for meaning).
   - Re-run `python scripts/add_student_tools.py` after regenerating any SAT study HTML so no page ships without it.

---

## 🏗️ Architecture Standard

When generating a simulator:
- **`index.html`**: Semantic markup, question containers, and toolbar controls.
- **`style.css` / Inline `<style>`**: Modern CSS variables, flexbox/grid layout, smooth animations.
- **`app.js` / Inline `<script>`**: Clean state management handling:
  - `state.currentQuestion`
  - `state.answers = { [qIndex]: selectedOption }`
  - `state.bookmarked = Set()`
  - `state.timeRemaining`
  - Score calculations and local storage caching.
