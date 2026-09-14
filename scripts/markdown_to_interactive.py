#!/usr/bin/env python3
"""
Markdown to Interactive Exam Simulator Compiler
Converts standard educational question banks and reading tests (IELTS, SAT, ESL)
into responsive, zero-dependency interactive HTML test simulators.
"""

import sys
import re
import json
from pathlib import Path

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent


def parse_markdown_quiz(md_content: str):
    """Parses markdown content into title, metadata, passage, questions, and rationales."""
    # 1. Extract Frontmatter
    metadata = {}
    if md_content.startswith("---"):
        parts = md_content.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    metadata[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2]
        else:
            body = md_content
    else:
        body = md_content

    # 2. Extract Title
    title_match = re.search(r"^#\s+(.+)$", body, re.M)
    title = title_match.group(1).strip() if title_match else metadata.get("topic", "Practice Module")
    title = re.sub(r"^[^\w\s]+", "", title).strip()

    # 3. Extract Passage if present (## PART 2 or ### The Architecture of... or ## Reading Passage)
    passage = ""
    passage_match = re.search(r"(?:##\s+(?:PART\s+2|Reading\s+Passage|Passage|Metin)[^\n]*\n)(.*?)(?=\n##\s+(?:PART\s+3|Questions|Sorular|Drill))", body, re.S | re.I)
    if passage_match:
        passage = passage_match.group(1).strip()
    
    # 4. Extract Questions
    # Looks for ### Question X or ### Soru X
    q_blocks = re.split(r"(?=###\s+(?:Question|Soru)\s+\d+)", body)
    questions = []
    
    # Also look for Answer Key section to extract answers and rationales
    answer_key_match = re.search(r"(?:##\s+(?:PART\s+4|Answer\s+Key|Cevap\s+Anahtarı|In-Depth\s+Distractor)[^\n]*\n)(.*)", body, re.S | re.I)
    answer_key_text = answer_key_match.group(1) if answer_key_match else ""

    # Parse answer key table if available
    # | Q1 | B | ... or | 1 | Noun | B | ...
    table_answers = {}
    for row in re.findall(r"\|\s*\*\*?(?:Q|S|Soru)?\s*(\d+)\*\*?\s*\|(?:[^|\n]*\|)*?\s*\*\*?([A-E])\*\*?\s*\|", answer_key_text):
        q_num, ans = row
        table_answers[int(q_num)] = ans.upper()

    # Parse distractor rationales if available
    # #### Question X or ### Soru X
    rationale_blocks = re.split(r"(?=###?#?\s+(?:Question|Soru)\s+\d+)", answer_key_text)
    rationale_map = {}
    for rb in rationale_blocks:
        rb_match = re.search(r"(?:Question|Soru)\s+(\d+)", rb)
        if rb_match:
            q_num = int(rb_match.group(1))
            rationale_map[q_num] = rb.strip()

    for block in q_blocks:
        match = re.search(r"###\s+(?:Question|Soru)\s+(\d+)[^\n]*\n+(.*?)(?=\n###|\n##|\Z)", block, re.S)
        if not match:
            continue
        q_num = int(match.group(1))
        q_content = match.group(2).strip()

        # Extract options: - **A)** Option text
        options = []
        option_lines = re.findall(r"[-*]\s+\*\*?([A-E])\)?\*\*?\s+(.*?)(?=\n[-*]\s+\*\*?[A-E]\)?\*\*?|\Z)", q_content, re.S)
        
        # Stem is everything before the first option
        stem_match = re.split(r"\n[-*]\s+\*\*?[A-E]\)?\*\*?", q_content)
        stem = stem_match[0].strip() if stem_match else q_content

        for opt_letter, opt_text in option_lines:
            options.append({
                "letter": opt_letter.strip().upper(),
                "text": opt_text.strip()
            })

        if options:
            correct = table_answers.get(q_num, "")
            explanation = rationale_map.get(q_num, "Rationale provided in module documentation.")
            questions.append({
                "number": q_num,
                "stem": stem,
                "options": options,
                "correct": correct,
                "explanation": explanation
            })

    return {
        "title": title,
        "metadata": metadata,
        "passage": passage,
        "questions": questions
    }


def build_interactive_html(parsed_data):
    """Compiles parsed quiz data into a single responsive HTML simulator."""
    data_json = json.dumps(parsed_data, ensure_ascii=False, indent=2)
    domain = parsed_data["metadata"].get("domain", "Exam")
    level = parsed_data["metadata"].get("target_level", "Standard")

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{parsed_data['title']} | Interactive Exam Simulator</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --primary-light: #eff6ff;
      --success: #16a34a;
      --success-light: #dcfce7;
      --danger: #dc2626;
      --danger-light: #fee2e2;
      --warning: #d97706;
      --warning-light: #fef3c7;
      --border: #e2e8f0;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05);
      --font: 'Plus Jakarta Sans', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    [data-theme="dark"] {{
      --bg: #0b0f19;
      --surface: #131b2e;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --primary: #3b82f6;
      --primary-hover: #60a5fa;
      --primary-light: #1e293b;
      --border: #334155;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.4);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      height: 100vh;
      display: flex;
      flex-direction: column;
    }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 0.75rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: var(--shadow);
      z-index: 10;
    }}

    .header-left {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .badge {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      background: var(--primary-light);
      color: var(--primary);
    }}

    .header-title {{
      font-size: 1.1rem;
      font-weight: 700;
    }}

    .header-controls {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .timer-box {{
      font-family: var(--font-mono);
      font-size: 1.1rem;
      font-weight: 700;
      padding: 6px 12px;
      border-radius: 8px;
      background: var(--primary-light);
      color: var(--primary);
    }}

    .btn {{
      padding: 8px 14px;
      border-radius: 8px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      cursor: pointer;
      font-weight: 600;
      font-size: 0.85rem;
      transition: all 0.2s;
    }}

    .btn:hover {{
      background: var(--primary-light);
      border-color: var(--primary);
    }}

    .btn-primary {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}

    .btn-primary:hover {{
      background: var(--primary-hover);
    }}

    .main-workspace {{
      flex: 1;
      display: grid;
      grid-template-columns: 1fr 1fr;
      overflow: hidden;
    }}

    .single-pane {{
      grid-template-columns: 1fr !important;
      max-width: 850px;
      margin: 0 auto;
      width: 100%;
    }}

    .pane {{
      overflow-y: auto;
      padding: 2rem;
    }}

    .pane-left {{
      border-right: 1px solid var(--border);
      background: var(--surface);
    }}

    .passage-content {{
      font-size: 1.05rem;
      line-height: 1.8;
      white-space: pre-wrap;
    }}

    .question-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 1.5rem;
      margin-bottom: 1.5rem;
      box-shadow: var(--shadow);
    }}

    .question-header {{
      display: flex;
      justify-content: space-between;
      margin-bottom: 1rem;
    }}

    .question-num {{
      font-weight: 700;
      color: var(--primary);
    }}

    .question-stem {{
      font-size: 1.05rem;
      font-weight: 600;
      margin-bottom: 1.25rem;
    }}

    .options-list {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}

    .option-item {{
      display: flex;
      align-items: flex-start;
      gap: 12px;
      padding: 12px 16px;
      border: 1px solid var(--border);
      border-radius: 8px;
      cursor: pointer;
      transition: all 0.2s;
    }}

    .option-item:hover {{
      background: var(--primary-light);
      border-color: var(--primary);
    }}

    .option-item.selected {{
      background: var(--primary-light);
      border-color: var(--primary);
      font-weight: 600;
    }}

    .option-item.correct {{
      background: var(--success-light);
      border-color: var(--success);
      color: var(--success);
      font-weight: 700;
    }}

    .option-item.incorrect {{
      background: var(--danger-light);
      border-color: var(--danger);
      color: var(--danger);
    }}

    .option-letter {{
      font-family: var(--font-mono);
      font-weight: 700;
      background: var(--bg);
      border: 1px solid var(--border);
      padding: 2px 8px;
      border-radius: 4px;
    }}

    .rationale-drawer {{
      margin-top: 1rem;
      padding: 1rem;
      border-radius: 8px;
      background: var(--bg);
      border-left: 4px solid var(--primary);
      display: none;
      font-size: 0.95rem;
    }}

    .nav-bar {{
      background: var(--surface);
      border-top: 1px solid var(--border);
      padding: 0.75rem 1.5rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .pill-container {{
      display: flex;
      gap: 6px;
      flex-wrap: wrap;
    }}

    .pill {{
      width: 32px;
      height: 32px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 6px;
      border: 1px solid var(--border);
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      font-family: var(--font-mono);
    }}

    .pill.answered {{ background: var(--primary-light); border-color: var(--primary); color: var(--primary); }}
    .pill.active {{ background: var(--primary); color: white; border-color: var(--primary); }}
  </style>
</head>
<body>

  <header>
    <div class="header-left">
      <span class="badge">{domain} • {level}</span>
      <h1 class="header-title">{parsed_data['title']}</h1>
    </div>
    <div class="header-controls">
      <div class="timer-box" id="timer">20:00</div>
      <button class="btn" onclick="toggleMode()" id="btnMode">Instant Feedback: OFF</button>
      <button class="btn" onclick="toggleTheme()">🌓</button>
      <button class="btn btn-primary" onclick="submitExam()">Submit Test</button>
    </div>
  </header>

  <div class="main-workspace {'single-pane' if not parsed_data['passage'] else ''}">
    {f'''
    <div class="pane pane-left">
      <h2 style="margin-bottom: 1rem; font-size: 1.3rem;">Reading Passage</h2>
      <div class="passage-content">{parsed_data['passage']}</div>
    </div>
    ''' if parsed_data['passage'] else ''}

    <div class="pane pane-right" id="questionsContainer">
      <!-- Injected by JS -->
    </div>
  </div>

  <div class="nav-bar">
    <div class="pill-container" id="pillsContainer"></div>
    <div>
      <span id="scoreDisplay" style="font-weight: 700; margin-right: 15px;"></span>
    </div>
  </div>

  <script>
    const quizData = {data_json};
    const userAnswers = {{}};
    let instantFeedback = false;
    let submitted = false;

    function renderQuestions() {{
      const container = document.getElementById('questionsContainer');
      const pills = document.getElementById('pillsContainer');

      container.innerHTML = quizData.questions.map((q, idx) => `
        <div class="question-card" id="qcard-${{idx}}">
          <div class="question-header">
            <span class="question-num">Question ${{q.number}}</span>
          </div>
          <div class="question-stem">${{q.stem}}</div>
          <div class="options-list">
            ${{q.options.map(opt => `
              <div class="option-item" id="opt-${{idx}}-${{opt.letter}}" onclick="selectOption(${{idx}}, '${{opt.letter}}')">
                <span class="option-letter">${{opt.letter}}</span>
                <span>${{opt.text}}</span>
              </div>
            `).join('')}}
          </div>
          <div class="rationale-drawer" id="rationale-${{idx}}">
            <strong>Solution Rationale:</strong>
            <p style="margin-top: 6px; white-space: pre-wrap;">${{q.explanation}}</p>
          </div>
        </div>
      `).join('');

      pills.innerHTML = quizData.questions.map((q, idx) => `
        <div class="pill" id="pill-${{idx}}" onclick="scrollToQuestion(${{idx}})">${{q.number}}</div>
      `).join('');
    }}

    function selectOption(qIdx, letter) {{
      if (submitted) return;
      userAnswers[qIdx] = letter;

      const q = quizData.questions[qIdx];
      q.options.forEach(opt => {{
        const el = document.getElementById(`opt-${{qIdx}}-${{opt.letter}}`);
        el.classList.remove('selected', 'correct', 'incorrect');
        if (opt.letter === letter) {{
          el.classList.add('selected');
        }}
      }});

      document.getElementById(`pill-${{qIdx}}`).classList.add('answered');

      if (instantFeedback) {{
        revealQuestionFeedback(qIdx);
      }}
    }}

    function revealQuestionFeedback(qIdx) {{
      const q = quizData.questions[qIdx];
      const selected = userAnswers[qIdx];
      const correct = q.correct;

      q.options.forEach(opt => {{
        const el = document.getElementById(`opt-${{qIdx}}-${{opt.letter}}`);
        if (opt.letter === correct) {{
          el.classList.add('correct');
        }} else if (opt.letter === selected && selected !== correct) {{
          el.classList.add('incorrect');
        }}
      }});

      document.getElementById(`rationale-${{qIdx}}`).style.display = 'block';
    }}

    function submitExam() {{
      submitted = true;
      let score = 0;
      quizData.questions.forEach((q, idx) => {{
        revealQuestionFeedback(idx);
        if (userAnswers[idx] === q.correct) {{
          score++;
        }}
      }});

      const total = quizData.questions.length;
      const pct = Math.round((score / total) * 100);
      document.getElementById('scoreDisplay').innerText = `Score: ${{score}} / ${{total}} (${{pct}}%)`;
      alert(`Test Submitted!\nYour Score: ${{score}} / ${{total}} (${{pct}}%)`);
    }}

    function toggleMode() {{
      instantFeedback = !instantFeedback;
      document.getElementById('btnMode').innerText = `Instant Feedback: ${{instantFeedback ? 'ON' : 'OFF'}}`;
      if (instantFeedback) {{
        Object.keys(userAnswers).forEach(idx => revealQuestionFeedback(Number(idx)));
      }}
    }}

    function toggleTheme() {{
      const current = document.documentElement.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      document.documentElement.setAttribute('data-theme', next);
    }}

    function scrollToQuestion(idx) {{
      document.getElementById(`qcard-${{idx}}`).scrollIntoView({{ behavior: 'smooth' }});
    }}

    // Timer
    let secondsLeft = 1200;
    setInterval(() => {{
      if (secondsLeft > 0 && !submitted) {{
        secondsLeft--;
        const mins = Math.floor(secondsLeft / 60);
        const secs = secondsLeft % 60;
        document.getElementById('timer').innerText = `${{mins.toString().padStart(2, '0')}}:${{secs.toString().padStart(2, '0')}}`;
      }}
    }}, 1000);

    renderQuestions();
  </script>
</body>
</html>
"""


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/markdown_to_interactive.py <path-to-markdown-file> [output-html-path]")
        sys.exit(1)

    md_path = Path(sys.argv[1])
    if not md_path.exists():
        print(f"Error: File '{md_path}' does not exist.")
        sys.exit(1)

    out_path = Path(sys.argv[2]) if len(sys.argv) > 2 else md_path.with_suffix(".html")
    
    print(f"Parsing '{md_path}'...")
    content = md_path.read_text(encoding="utf-8")
    parsed_data = parse_markdown_quiz(content)

    print(f"Generating interactive simulator with {len(parsed_data['questions'])} questions...")
    html_output = build_interactive_html(parsed_data)

    out_path.write_text(html_output, encoding="utf-8")
    print(f"[+] Successfully created interactive simulator at: {out_path}")


if __name__ == "__main__":
    main()
