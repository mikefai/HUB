---
name: pedagogical-quality-linter
description: >-
  Quality audit and verification runbook for educational content. Checks YAML
  metadata validity, distractor quality, CEFR/IELTS/SAT alignment, and
  ensures comprehensive pedagogical scaffolding.
---

# 🔍 Pedagogical Quality Linter Skill

Use this skill to inspect, audit, and improve any educational markdown document or question bank.

---

## 📋 Quality Checklist

### 1. Metadata Verification
- [ ] Contains valid YAML frontmatter at line 1 (`--- ... ---`).
- [ ] Has valid `domain` matching one of `ESL`, `IELTS`, `SAT`.
- [ ] Declares appropriate `target_level` (e.g. `CEFR B2`, `Band 6.0 to 7.0`, `Score 700+`).
- [ ] Has accurate `content_type` (`Lesson Plan`, `Worksheet`, `Drill`, `Mock Test`, `Model Essay`).
- [ ] Saved inside the matching directory path according to the domain routing table.

### 2. Distractor & Answer Key Standards
- [ ] **Exact Option Count**:
  - SAT: Exactly 4 options (`A`, `B`, `C`, `D`).
  - IELTS / ESL: Standard 4 options (`A`, `B`, `C`, `D`) or True/False/Not Given format.
- [ ] **No Obvious "All/None of the above"**: Avoid lazy distractors.
- [ ] **Distractor Analysis**: Every question MUST provide a rationale explaining:
  1. Why the correct answer is unambiguously correct.
  2. The specific flaw in each distractor (e.g., *Trap 1: Verbatim Echo*, *Trap 2: Direct Contradiction*, *Trap 3: Not Given / Out of Scope*, *Trap 4: Extreme Language*, *Trap 5: Partial Truth*).

### 3. ESL Scaffolding Checks
- [ ] Target grammar/lexis clearly defined with Concept Check Questions (CCQs).
- [ ] Pronunciation, form, and meaning covered before practice.
- [ ] Realistic timing breakdowns included for 45/60/90 minute lesson blocks in `Lesson_Flow/` or CEFR level folders.

### 4. IELTS / SAT Authenticity Checks
- [ ] IELTS: Strictly IELTS Academic standards, official word count floors (Task 1: min 150 words, Task 2: min 250 words) and band descriptors.
- [ ] SAT: Reading/Writing passages conform to College Board single-paragraph stimuli (25–150 words).
