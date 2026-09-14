---
name: content-creation-pipeline
description: >-
  Master workflow for designing and generating structured educational content,
  lesson plans, question sets, and exam preparation materials across ESL, IELTS Academic,
  and Digital SAT. Enforces pedagogical scaffolding, authentic
  rubric alignment, and complete distractor rationales.
---

# 🎓 Content Creation Pipeline Skill

This skill provides step-by-step procedures for generating curriculum-aligned, exam-accurate pedagogical content across the three core domains:
1. **ESL** (CEFR A1, A2, B1, B2, C1, C2 & Lesson Flow)
2. **IELTS** (IELTS Academic Exclusively - Band 5.0 to 6.0, Band 6.0 to 7.0, Band 7.0 to 8.0, Band 8.0 to 9.0)
3. **SAT** (Digital SAT Reading/Writing & Math)

---

## 🧭 Step 1: Domain & Level Determination

Always verify the user's target domain and difficulty level before generating materials:

| Domain | Target Parameter | Standard Reference |
| :--- | :--- | :--- |
| **ESL** | CEFR Level & Flow | `A1`, `A2`, `B1`, `B2`, `C1`, `C2`, `Lesson_Flow` |
| **IELTS** | Target Band Progression | `Band 5.0 to 6.0`, `Band 6.0 to 7.0`, `Band 7.0 to 8.0`, `Band 8.0 to 9.0` (Academic only) |
| **SAT** | Score Range & Domain | Score 600–800 (Reading/Writing vs Math; Craft & Structure, Info & Ideas, SEC, Expression) |

---

## 📝 Step 2: Content Scaffolding Workflows

### 1. ESL Lesson Flow & CEFR Modules
- **Warm-Up / Lead-In (5–10 mins)**: Activate schemata, communicative hook.
- **Presentation / Clarification (15–20 mins)**: Meaning, Form, Pronunciation (MFP), and Concept Check Questions (CCQs).
- **Controlled Practice (15–20 mins)**: Gap-fills, matching, accuracy drills with immediate feedback.
- **Freer Production (20–25 mins)**: Communicative task, pair speaking, or personalized writing.
- **Wrap-Up & Error Correction (5–10 mins)**: Delayed error feedback and key takeaways.

### 2. IELTS Academic Skill & Band Transitions
- **Band Progression Focus**: Address the exact linguistic gaps between the learner's current band and target band.
- **Academic Task 1**: Single visual stimulus (graph/chart/process/map), 150+ words, 4-paragraph structure (Intro paraphrase, Overview with 2 key features, 2 Detailed body paragraphs comparing data).
- **Academic Task 2**: Clear essay prompt, 250+ words, 4-paragraph structure (Intro with thesis, 2 fully developed main body paragraphs with specific examples, Conclusion).
- **Examiner Commentary Matrix**: Explicit assessment breakdown across **TR/TA**, **CC**, **LR**, and **GRA**.

### 3. Digital SAT Question Item Sets
- **Stimulus Length**: 25–150 words per single-passage item.
- **4 Options**: `A`, `B`, `C`, `D` with equal plausibility.
- **Comprehensive Explanations**:
  - Direct textual / grammatical rationale for the correct answer.
  - Granular distractor analysis explaining the specific trap (e.g. *Opposite Claim*, *Verbatim Echo*, *Not Supported*, *Faulty Modifier*).

---

## 🏷️ Step 3: Mandatory Metadata & File Saving

Every generated file MUST start with YAML frontmatter:
```yaml
---
domain: "ESL | IELTS | SAT"
target_level: "[Level / Band Transition / Score]"
topic: "[Specific Subject / Topic]"
date_created: "YYYY-MM-DD"
content_type: "Lesson Plan | Worksheet | Drill | Mock Test | Model Essay | Analysis"
---
```

Save into the matching domain directory:
- ESL: `ESL/[A1|A2|B1|B2|C1|C2|Lesson_Flow]/`
- IELTS: `IELTS/[Reading|Writing_Task1|Writing_Task2|Listening|Speaking]/<Band_Transition>/` (or `Mock_Tests/`, `Vocabulary_Collocations/`)
- SAT: `SAT/[Reading_Writing|Math|Question_Banks|Practice_Modules]/`
