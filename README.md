# 🎓 AG Teaching & Exam Prep Hub

Structured curriculum + interactive exam simulators across **3 domains**: **ESL**, **IELTS Academic**, **Digital SAT**.

- 🌐 **Master portal (deployed on Vercel):** [`index.html`](./index.html)
- 🔗 **GitHub repo:** [`mikefai/HUB`](https://github.com/mikefai/HUB)

## 🧭 Portal wiring

```
content page (.md + .html) → domain hub → master portal (index.html)
ESL/*   → ESL/index.html   ↘
IELTS/* → IELTS/index.html → index.html (Vercel)
SAT/*   → SAT/index.html   ↗
```

Every content page links to its domain hub, and each hub links up to the master portal.
All links are **relative**, so the static output deploys on Vercel unchanged.

## 📁 Domains

| Domain | Hub | Content |
| :--- | :--- | :--- |
| 🌍 **ESL** (CEFR A1–C2, PPP/TBLT) | [`ESL/index.html`](ESL/index.html) | `ESL/A1/ … ESL/C2/`, `ESL/Lesson_Flow/` |
| 🎯 **IELTS Academic** (Band 5.0→9.0) | [`IELTS/index.html`](IELTS/index.html) | `Reading/`, `Writing_Task1/`, `Writing_Task2/`, `Listening/`, `Speaking/`, `Mock_Tests/`, `Vocabulary_Collocations/` |
| 🏛️ **Digital SAT** (College Board) | [`SAT/index.html`](SAT/index.html) | `Reading_Writing/`, `Math/`, `Question_Banks/`, `Practice_Modules/` |

Full catalog: [`WORKSPACE_INDEX.md`](WORKSPACE_INDEX.md) (auto-generated).

## 🛠️ Automation

```bash
python scripts/validate_workspace.py      # frontmatter + routing + answer-key audit
python scripts/build_workspace_index.py   # regenerate ESL/IELTS/SAT hubs + index.html + WORKSPACE_INDEX.md
```

## 🚀 Deploy on Vercel

1. Push this folder to [`mikefai/HUB`](https://github.com/mikefai/HUB) (already wired into `README.md` and `scripts/build_workspace_index.py` → `SITE_REPO_URL`).
2. Vercel → **Add New Project** → import the repo. No build step needed (static).
3. `vercel.json` enables clean URLs (e.g. `/IELTS` serves `IELTS/index.html`).

Local preview: open `index.html` directly, or `npx vercel dev`.
