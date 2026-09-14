# Automatic Content Routing & Exam Preparation Rules

## Intent Detection & Folder Dispatch
Whenever a request is received to generate, draft, or edit educational content:
1. Scan prompt for domain keywords:
   - **IELTS**: Route directly to `IELTS/` (Strictly IELTS Academic: `Reading/`, `Writing_Task1/`, `Writing_Task2/`, `Listening/`, `Speaking/` with `Band_5.0_to_6.0/`, `Band_6.0_to_7.0/`, `Band_7.0_to_8.0/`, `Band_8.0_to_9.0/`, plus `Mock_Tests/`, `Vocabulary_Collocations/`).
   - **ESL**: Route directly to `ESL/` (`A1/`, `A2/`, `B1/`, `B2/`, `C1/`, `C2/`, `Lesson_Flow/`).
    - **SAT**: Route directly to `SAT/` (`Reading_Writing/`, `Math/`, `Question_Banks/`, `Practice_Modules/`).

2. Portal Wiring (Vercel deployment):
    - Every content page links to its domain hub (`ESL/index.html`, `IELTS/index.html`, `SAT/index.html`).
    - Each domain hub links up to the master portal (`index.html`), which is deployed on Vercel.

3. Format & Quality Requirements:
    - Always include YAML metadata header specifying domain (`ESL`, `IELTS`, `SAT`), target level/band, topic, date, and content type.
   - Always include complete answer keys and in-depth distractor rationales for practice questions.
   - Use the pre-built templates in `Templates/` for high-frequency formats.

4. Post-Creation Automation:
   - Run `python scripts/validate_workspace.py` to ensure schema compliance.
   - Run `python scripts/build_workspace_index.py` to refresh `WORKSPACE_INDEX.md` and `index.html`.
