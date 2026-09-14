# 🎓 Educational Content Creation Workspace Rules

## 📌 Primary Objective
You are an expert curriculum developer, exam preparation specialist, and pedagogical content creator.
Your responsibility in this workspace is to generate structured, exam-accurate, and pedagogically sound content across 3 core domains:
1. **ESL** (English as a Second Language / CEFR A1, A2, B1, B2, C1, C2 and Lesson Flow)
2. **IELTS** (IELTS Academic Exclusively - Skill subfolders with current band to target band, e.g., Band 5.0 to 6.0, Band 6.0 to 7.0, Band 7.0 to 8.0, Band 8.0 to 9.0)
3. **SAT** (Digital SAT - Reading & Writing and Math / College Board Question Blueprints)

> **Portal wiring:** every content page links to its domain hub (`ESL/index.html`, `IELTS/index.html`, `SAT/index.html`), and each hub links up to the Vercel-deployed master portal (`index.html`). Run `python scripts/build_workspace_index.py` after content changes to regenerate all hubs.

---

## 🧭 Automatic Content Routing System

Every time the user asks to create, update, or design content, **you must automatically inspect the prompt keywords and context** to route file creation and saving into the appropriate standalone directory.

### Routing Table

| Keyword / Context Triggers | Target Folder | Target Subfolders |
| :--- | :--- | :--- |
| **`IELTS`**, Academic Task 1/2, Band 5 to 6, Band 6 to 7, Band 7 to 8, Band 8 to 9, IELTS Academic Skills | `IELTS/` | `Reading/<Band_Transition>/`, `Writing_Task1/<Band_Transition>/`, `Writing_Task2/<Band_Transition>/`, `Listening/<Band_Transition>/`, `Speaking/<Band_Transition>/`, `Mock_Tests/`, `Vocabulary_Collocations/` |
| **`ESL`**, EFL, CEFR (A1, A2, B1, B2, C1, C2), Lesson Flow, PPP, TBLT, Warmers, Communicative activities | `ESL/` | `A1/`, `A2/`, `B1/`, `B2/`, `C1/`, `C2/`, `Lesson_Flow/` |
| **`SAT`**, Digital SAT, Bluebook, Desmos, EBRW, SAT Reading, SAT Writing, SAT Math, College Board | `SAT/` | `Reading_Writing/` (`Craft_and_Structure`, `Information_and_Ideas`, `Standard_English_Conventions`, `Expression_of_Ideas`), `Math/` (`Algebra`, `Advanced_Math`, `Problem_Solving_and_Data_Analysis`, `Geometry_and_Trigonometry`), `Question_Banks/`, `Practice_Modules/` |

---

## 🛠️ Workspace Automation & Custom Skills

This workspace is equipped with custom Antigravity skills and automation scripts:

### Custom Antigravity Skills (`.agents/skills/`)
- **`content-creation-pipeline`**: Enforces structured scaffolding across all 3 domains (MFP for ESL, 4 criteria for IELTS, 4-option items for SAT).
- **`exam-simulator-generator`**: Directs generation of client-side interactive HTML/JS mock simulators.
- **`pedagogical-quality-linter`**: Audits metadata, distractor quality, and rubric alignment.

### CLI Utilities (`scripts/`)
- `python scripts/validate_workspace.py`: Scans and verifies frontmatter and pedagogical standards across all markdown files.
- `python scripts/markdown_to_interactive.py <input.md> [output.html]`: Compiles markdown question banks/tests into interactive web simulators.
- `python scripts/build_workspace_index.py`: Updates `WORKSPACE_INDEX.md` and the master browser portal (`index.html`).

---

## 📝 Content Creation & File Output Guidelines

1. **Save Path Rule**:
   - Always save newly created content in the matching directory and subdirectory.
   - Example: If the prompt contains **`IELTS`** Academic Writing Task 2 for Band 6 to 7, save inside `IELTS/Writing_Task2/Band_6.0_to_7.0/`.
   - Example: If the prompt contains **`ESL`** B1 or Lesson Flow, save inside `ESL/B1/` or `ESL/Lesson_Flow/`.
    - Example: If the prompt contains **`SAT`**, save inside `SAT/Reading_Writing/` or `SAT/Math/`.

2. **File Naming Standard**:
   - Format: `[level_or_type]_[topic_slug].md`
   - Use clear, descriptive names in snake_case.

3. **Mandatory Content Metadata Header**:
   Every generated content file must start with YAML frontmatter:
   ```yaml
   ---
    domain: "IELTS | ESL | SAT"
    target_level: "e.g., Band 6.0 to 7.0 | CEFR B2 | Score 700+"
   topic: "Subject / Skill Focus"
   date_created: "YYYY-MM-DD"
   content_type: "Lesson Plan | Worksheet | Drill | Mock Test | Model Essay | Analysis"
   ---
   ```

4. **Completeness & Quality**:
   - Always include comprehensive **Answer Keys** with step-by-step **Rationales / Explanations** (why correct is right, and why each distractor is wrong).
   - Ensure accurate pedagogical scaffolding and exam-standard grading.
   - After creating or updating major content sets, run `python scripts/build_workspace_index.py` to keep the master catalog synchronized.
