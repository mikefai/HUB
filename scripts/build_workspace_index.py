#!/usr/bin/env python3
"""
Workspace Index & Independent Portal Builder
Scans the workspace for educational markdown files and interactive HTML simulators,
then generates:
1. ESL/index.html (Dedicated ESL Curriculum Portal — hub for ALL ESL content)
2. IELTS/index.html (Dedicated IELTS Academic Portal linked to https://github.com/mikefai/AG-IELTS-Academic — hub for ALL IELTS content)
3. SAT/index.html (Dedicated Digital SAT Portal linked to https://github.com/mikefai/AG-SAT — hub for ALL SAT content)
4. Root index.html (Master Educational Workspace Hub — deployed on Vercel, links to the 3 domain portals)
5. WORKSPACE_INDEX.md (Master Markdown Catalog)

Wiring: content pages -> domain portal (ESL/IELTS/SAT index.html) -> root index.html.
All links are relative so the static output deploys unchanged on Vercel (see vercel.json).
Set SITE_REPO_URL below to the new GitHub repo URL for the Vercel deployment.
"""

import os
import sys
import re
import json
from pathlib import Path
from datetime import datetime

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DOMAINS = ["ESL", "IELTS", "SAT"]
EXCLUDED_MD = {"README.md", "AGENTS.md", "GEMINI.md", "WORKSPACE_INDEX.md", "routing.md"}

# GitHub repo backing the Vercel deployment of the root index.html.
SITE_REPO_URL = "https://github.com/mikefai/HUB"

# Domain configurations & GitHub repository links
DOMAIN_CONFIGS = {
    "IELTS": {
        "title": "IELTS Academic Prep Portal",
        "subtitle": "Band 5.0 to 9.0 Scaffolded Curriculum, Model Essays & Interactive Simulators",
        "repo_url": "https://github.com/mikefai/AG-IELTS-Academic",
        "icon": "🎯",
        "color": "#ef4444",
        "tagline": "Academic Reading • Writing Task 1 & 2 • Speaking • Listening • Band Descriptors",
        "categories": [
            "Reading",
            "Writing_Task1",
            "Writing_Task2",
            "Speaking",
            "Listening",
            "Vocabulary_Collocations",
            "Mock_Tests"
        ],
        "band_levels": [
            "Band 5.0 to 6.0",
            "Band 6.0 to 7.0",
            "Band 7.0 to 8.0",
            "Band 8.0 to 9.0"
        ]
    },
    "SAT": {
        "title": "Digital SAT Prep Portal",
        "subtitle": "College Board Bluebook Aligned Reading & Writing and Math Modules",
        "repo_url": "https://github.com/mikefai/AG-SAT",
        "icon": "🏛️",
        "color": "#8b5cf6",
        "tagline": "Reading & Writing (Craft & Structure, Info & Ideas, SEC, Expression) • Math (Algebra, Adv Math, Data, Geom)",
        "categories": [
            "Reading_Writing",
            "Craft_and_Structure",
            "Information_and_Ideas",
            "Standard_English_Conventions",
            "Expression_of_Ideas",
            "Math",
            "Algebra",
            "Advanced_Math",
            "Problem_Solving_and_Data_Analysis",
            "Geometry_and_Trigonometry",
            "Practice_Modules",
            "Question_Banks"
        ],
        "band_levels": [
            "Score 600+",
            "Score 700+",
            "Score 750+",
            "Score 800 Target"
        ]
    },
    "ESL": {
        "title": "ESL Curriculum & Lesson Flow Portal",
        "subtitle": "CEFR A1–C2 Communicative Lesson Plans, TBLT Labs & Grammar Worksheets",
        "repo_url": None,
        "icon": "🌍",
        "color": "#10b981",
        "tagline": "CEFR A1, A2, B1, B2, C1, C2 • PPP & TBLT Lesson Flows • Interactive Speaking Labs",
        "categories": [
            "A1", "A2", "B1", "B2", "C1", "C2", "Lesson_Flow", "Grammar", "Vocabulary", "Reading", "Speaking_Listening"
        ],
        "band_levels": [
            "CEFR A1", "CEFR A2", "CEFR B1", "CEFR B2", "CEFR C1", "CEFR C2"
        ]
    },
}


def extract_frontmatter(content: str):
    if not content.startswith("---"):
        return {}
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}
    metadata = {}
    for line in parts[1].strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            k, v = line.split(":", 1)
            metadata[k.strip()] = v.strip().strip('"').strip("'")
    return metadata


def scan_workspace():
    items = []
    
    # 1. Scan Markdown content
    for domain in DOMAINS:
        domain_dir = WORKSPACE_ROOT / domain
        if not domain_dir.exists():
            continue
        for md_file in domain_dir.rglob("*.md"):
            if md_file.name in EXCLUDED_MD:
                continue
            try:
                content = md_file.read_text(encoding="utf-8")
                meta = extract_frontmatter(content)
                title_match = re.search(r"^#\s+(.+)$", content, re.M)
                title = title_match.group(1).strip() if title_match else md_file.stem.replace("_", " ").title()
                title = re.sub(r"^[^\w\s]+", "", title).strip()

                rel_to_root = md_file.relative_to(WORKSPACE_ROOT).as_posix()
                rel_to_domain = md_file.relative_to(domain_dir).as_posix()

                # Button link: prefer the rendered HTML twin. Browsers cannot
                # render raw .md as a study page, and every content .md ships
                # with a paired .html page (verified: zero orphan MDs).
                html_twin = md_file.with_suffix(".html")
                if html_twin.exists():
                    link_root = html_twin.relative_to(WORKSPACE_ROOT).as_posix()
                    link_domain = html_twin.relative_to(domain_dir).as_posix()
                else:
                    link_root = rel_to_root
                    link_domain = rel_to_domain

                # Determine subcategory / folder tags
                parts = md_file.relative_to(domain_dir).parts
                category = parts[0] if len(parts) > 1 else "General"
                sub_category = parts[1] if len(parts) > 2 else ""

                items.append({
                    "title": title or md_file.stem,
                    "domain": meta.get("domain", domain).upper(),
                    "target_level": meta.get("target_level", "All Levels"),
                    "topic": meta.get("topic", md_file.stem.replace("_", " ").title()),
                    "date_created": meta.get("date_created", "2026"),
                    "content_type": meta.get("content_type", "Document"),
                    "path_root": rel_to_root,
                    "path_domain": rel_to_domain,
                    "link_root": link_root,
                    "link_domain": link_domain,
                    "category": category,
                    "sub_category": sub_category,
                    "is_interactive": False,
                    "file_type": "Markdown",
                    "filename": md_file.name
                })
            except Exception as e:
                print(f"Error reading {md_file}: {e}")

    # 2. Scan Interactive HTML simulators
    # Dedupe: an HTML page with an indexed .md twin does NOT get its own card —
    # the MD card already links to the HTML twin (link_root/link_domain).
    md_indexed = {it["path_root"] for it in items}
    for html_file in WORKSPACE_ROOT.rglob("*.html"):
        if html_file.name in {"index.html", "README.html"}:
            continue
        if any(part.startswith(".") for part in html_file.parts):
            continue
        twin = html_file.with_suffix(".md")
        try:
            twin_rel = twin.relative_to(WORKSPACE_ROOT).as_posix()
        except ValueError:
            twin_rel = None
        if twin_rel and twin_rel in md_indexed:
            continue
        try:
            content = html_file.read_text(encoding="utf-8")
            title_match = re.search(r"<title>(.*?)</title>", content, re.I | re.S)
            title = title_match.group(1).strip() if title_match else html_file.stem.replace("_", " ").title()
            
            domain = "General"
            domain_dir = None
            for d in DOMAINS:
                if d in html_file.parts:
                    domain = d
                    domain_dir = WORKSPACE_ROOT / d
                    break

            rel_to_root = html_file.relative_to(WORKSPACE_ROOT).as_posix()
            rel_to_domain = html_file.relative_to(domain_dir).as_posix() if domain_dir else rel_to_root

            parts = html_file.relative_to(domain_dir).parts if domain_dir else []
            category = parts[0] if len(parts) > 1 else "Interactive App"
            sub_category = parts[1] if len(parts) > 2 else ""

            items.append({
                "title": title,
                "domain": domain.upper(),
                "target_level": "Interactive Webapp",
                "topic": html_file.stem.replace("_", " ").title(),
                "date_created": "2026",
                "content_type": "Interactive Simulator",
                    "path_root": rel_to_root,
                    "path_domain": rel_to_domain,
                    "link_root": rel_to_root,
                    "link_domain": rel_to_domain,
                    "category": category,
                    "sub_category": sub_category,
                    "is_interactive": True,
                "file_type": "HTML Simulator",
                "filename": html_file.name
            })
        except Exception as e:
            print(f"Error reading {html_file}: {e}")

    return items


def generate_domain_portal_html(domain: str, items: list):
    config = DOMAIN_CONFIGS.get(domain, {
        "title": f"{domain} Workspace Portal",
        "subtitle": f"Curriculum & Interactive Resources for {domain}",
        "repo_url": None,
        "icon": "📁",
        "color": "#3b82f6",
        "tagline": "Standalone Domain Preparation & Resources",
        "categories": [],
        "band_levels": []
    })

    domain_items = [it for it in items if it["domain"].upper() == domain.upper()]
    items_json = json.dumps(domain_items, ensure_ascii=False, indent=2)
    repo_url = config.get("repo_url")

    repo_button_html = f"""
      <a href="{repo_url}" target="_blank" rel="noopener noreferrer" class="btn-github">
        <svg height="18" width="18" viewBox="0 0 16 16" fill="currentColor"><path d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path></svg>
        GitHub Repository
      </a>
    """ if repo_url else ""

    extra_tools_section = ""
    if domain == "IELTS":
        extra_tools_section = """
        <div class="helper-box">
          <div class="helper-header">
            <h3>📊 IELTS Band Score & Assessment Reference</h3>
            <span class="badge">Academic Rubric</span>
          </div>
          <div class="helper-grid">
            <div class="helper-item">
              <strong>Task Achievement / Response (25%)</strong>
              <p>Fully addresses all prompt parts, presents a well-developed position with supported main ideas.</p>
            </div>
            <div class="helper-item">
              <strong>Coherence & Cohesion (25%)</strong>
              <p>Sequences information logically, clear progression, paragraphing, and seamless cohesive markers.</p>
            </div>
            <div class="helper-item">
              <strong>Lexical Resource (25%)</strong>
              <p>Wide natural vocabulary, sophisticated collocations, accurate paraphrasing, precise register.</p>
            </div>
            <div class="helper-item">
              <strong>Grammar Range & Accuracy (25%)</strong>
              <p>Mix of complex sentence structures, high proportion of error-free sentences, accurate punctuation.</p>
            </div>
          </div>
        </div>
        """
    elif domain == "SAT":
        extra_tools_section = """
        <div class="helper-box">
          <div class="helper-header">
            <h3>🏛️ Digital SAT Structure & College Board Specification</h3>
            <span class="badge">Adaptive Blueprint</span>
          </div>
          <div class="helper-grid">
            <div class="helper-item">
              <strong>Reading & Writing (2 Modules)</strong>
              <p>54 Questions • 64 Minutes total. Craft & Structure, Information & Ideas, Standard English Conventions, Expression of Ideas.</p>
            </div>
            <div class="helper-item">
              <strong>Math (2 Modules)</strong>
              <p>44 Questions • 70 Minutes total. Algebra, Advanced Math, Problem Solving & Data Analysis, Geometry & Trig. Desmos allowed throughout.</p>
            </div>
            <div class="helper-item">
              <strong>Scoring Scale</strong>
              <p>Total: 400–1600 (EBRW: 200–800, Math: 200–800). Section-adaptive routing based on Module 1 performance.</p>
            </div>
            <div class="helper-item">
              <strong>Item Design Rules</strong>
              <p>Single short stimuli (25–150 words), 4-option multiple choice or student-produced responses (Math).</p>
            </div>
          </div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{config['title']} | AG Workspace</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: {config['color']};
      --primary-hover: #1e293b;
      --primary-light: rgba(59, 130, 246, 0.08);
      --border: #e2e8f0;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
      --radius: 12px;
      --font: 'Plus Jakarta Sans', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    [data-theme="dark"] {{
      --bg: #0b0f19;
      --surface: #131b2e;
      --card-bg: #1e293b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --primary-light: rgba(255, 255, 255, 0.05);
      --border: #334155;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding-bottom: 60px;
    }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.25rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow);
    }}

    .header-content {{
      max-width: 1240px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 15px;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 14px;
      text-decoration: none;
      color: inherit;
    }}

    .brand-icon {{
      background: {config['color']};
      color: white;
      font-size: 1.4rem;
      width: 44px;
      height: 44px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 10px;
      font-weight: 800;
    }}

    .brand h1 {{
      font-size: 1.2rem;
      font-weight: 700;
    }}

    .brand p {{
      font-size: 0.8rem;
      color: var(--text-muted);
    }}

    .header-actions {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .btn-nav {{
      background: var(--surface);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
      font-size: 0.85rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 6px;
      transition: all 0.2s;
    }}

    .btn-nav:hover {{
      background: var(--primary-light);
      border-color: var(--primary);
    }}

    .btn-github {{
      background: #24292f;
      color: #ffffff;
      padding: 8px 14px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.85rem;
      text-decoration: none;
      display: inline-flex;
      align-items: center;
      gap: 8px;
      transition: background 0.2s;
    }}

    .btn-github:hover {{
      background: #000000;
    }}

    main {{
      max-width: 1240px;
      margin: 2rem auto;
      padding: 0 1.5rem;
    }}

    .hero-banner {{
      background: linear-gradient(135deg, {config['color']}15, rgba(59, 130, 246, 0.05));
      border: 1px solid var(--border);
      border-left: 6px solid {config['color']};
      border-radius: var(--radius);
      padding: 2rem;
      margin-bottom: 2rem;
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 20px;
    }}

    .hero-text h2 {{
      font-size: 1.7rem;
      font-weight: 800;
      margin-bottom: 0.4rem;
    }}

    .hero-text p {{
      color: var(--text-muted);
      max-width: 700px;
      font-size: 0.95rem;
    }}

    .stats-container {{
      display: flex;
      gap: 1.5rem;
    }}

    .stat-pill {{
      background: var(--surface);
      border: 1px solid var(--border);
      padding: 10px 18px;
      border-radius: var(--radius);
      text-align: center;
      box-shadow: var(--shadow);
    }}

    .stat-val {{
      font-size: 1.5rem;
      font-weight: 800;
      color: {config['color']};
    }}

    .stat-lbl {{
      font-size: 0.75rem;
      color: var(--text-muted);
      text-transform: uppercase;
      font-weight: 700;
    }}

    .filter-section {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.25rem;
      margin-bottom: 2rem;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      gap: 12px;
    }}

    .filter-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      align-items: center;
    }}

    .filter-label {{
      font-size: 0.8rem;
      font-weight: 700;
      color: var(--text-muted);
      text-transform: uppercase;
      margin-right: 6px;
      min-width: 90px;
    }}

    .filter-btn {{
      background: var(--bg);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 6px 14px;
      border-radius: 16px;
      cursor: pointer;
      font-size: 0.85rem;
      font-weight: 600;
      transition: all 0.15s ease;
    }}

    .filter-btn:hover {{
      border-color: {config['color']};
    }}

    .filter-btn.active {{
      background: {config['color']};
      color: white;
      border-color: {config['color']};
    }}

    .search-box {{
      width: 100%;
      padding: 12px 18px;
      border-radius: 10px;
      border: 1px solid var(--border);
      background: var(--bg);
      color: var(--text);
      font-family: inherit;
      font-size: 0.95rem;
    }}

    .card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .content-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .content-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
      border-color: {config['color']}88;
    }}

    .card-top {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}

    .cat-badge {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      background: {config['color']}18;
      color: {config['color']};
      text-transform: uppercase;
    }}

    .level-tag {{
      font-size: 0.75rem;
      font-family: var(--font-mono);
      color: var(--text-muted);
      background: var(--bg);
      padding: 3px 8px;
      border-radius: 4px;
      border: 1px solid var(--border);
    }}

    .card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }}

    .card-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }}

    .card-actions {{
      display: flex;
      gap: 10px;
    }}

    .btn-launch {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 600;
      font-size: 0.9rem;
      text-decoration: none;
      background: {config['color']};
      color: white;
      transition: opacity 0.2s;
    }}

    .btn-launch:hover {{
      opacity: 0.9;
    }}

    .btn-interactive {{
      background: linear-gradient(135deg, #10b981, #059669);
    }}

    .helper-box {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.75rem;
      margin-top: 2rem;
      box-shadow: var(--shadow);
    }}

    .helper-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }}

    .helper-header h3 {{
      font-size: 1.15rem;
      font-weight: 700;
    }}

    .helper-header .badge {{
      font-size: 0.75rem;
      background: {config['color']}22;
      color: {config['color']};
      padding: 4px 10px;
      border-radius: 6px;
      font-weight: 700;
    }}

    .helper-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 1.25rem;
    }}

    .helper-item {{
      background: var(--bg);
      border: 1px solid var(--border);
      padding: 1.2rem;
      border-radius: 10px;
    }}

    .helper-item strong {{
      display: block;
      font-size: 0.95rem;
      margin-bottom: 0.35rem;
      color: {config['color']};
    }}

    .helper-item p {{
      font-size: 0.85rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    footer {{
      margin-top: 3rem;
      text-align: center;
      font-size: 0.85rem;
      color: var(--text-muted);
      border-top: 1px solid var(--border);
      padding-top: 1.5rem;
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <a href="../index.html" class="brand">
        <div class="brand-icon">{config['icon']}</div>
        <div>
          <h1>{config['title']}</h1>
          <p>{config['tagline']}</p>
        </div>
      </a>
      <div class="header-actions">
        <a href="../index.html" class="btn-nav">🏠 Main Hub</a>
        {repo_button_html}
        <button class="btn-nav" id="themeToggle" onclick="toggleTheme()">🌓 Theme</button>
      </div>
    </div>
  </header>

  <main>
    <div class="hero-banner">
      <div class="hero-text">
        <h2>{config['title']}</h2>
        <p>{config['subtitle']}</p>
      </div>
      <div class="stats-container">
        <div class="stat-pill">
          <div class="stat-val" id="totalCount">{len(domain_items)}</div>
          <div class="stat-lbl">Creations</div>
        </div>
        <div class="stat-pill">
          <div class="stat-val" id="interactiveCount" style="color: #10b981;">{sum(1 for i in domain_items if i['is_interactive'])}</div>
          <div class="stat-lbl">Interactive Apps</div>
        </div>
      </div>
    </div>

    <div class="filter-section">
      <div class="filter-row">
        <span class="filter-label">Skill / Area:</span>
        <button class="filter-btn active" onclick="filterCategory('ALL')">All Categories</button>
        {' '.join(f'<button class="filter-btn" onclick="filterCategory(\'{cat}\')">{cat.replace("_", " ")}</button>' for cat in config['categories'])}
        <button class="filter-btn" onclick="filterInteractive()">🚀 Interactive Simulators</button>
      </div>
      <div class="filter-row">
        <span class="filter-label">Target Level:</span>
        <button class="filter-btn active" onclick="filterLevel('ALL')">All Levels</button>
        {' '.join(f'<button class="filter-btn" onclick="filterLevel(\'{lvl}\')">{lvl}</button>' for lvl in config['band_levels'])}
      </div>
      <input type="text" class="search-box" id="searchBox" placeholder="🔍 Search {domain} modules, questions, topics..." oninput="handleSearch()">
    </div>

    <div class="card-grid" id="contentGrid">
      <!-- Dynamically injected -->
    </div>

    {extra_tools_section}

    <footer>
      <p>AG Educational Content Engine • {config['title']} • Auto-synchronized with workspace files</p>
    </footer>
  </main>

  <script>
    const items = {items_json};

    let activeCategory = 'ALL';
    let activeLevel = 'ALL';
    let onlyInteractive = false;
    let searchQuery = '';

    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('ag_theme', next);
    }}

    const savedTheme = localStorage.getItem('ag_theme');
    if (savedTheme) {{
      document.documentElement.setAttribute('data-theme', savedTheme);
    }}

    function renderGrid() {{
      const grid = document.getElementById('contentGrid');
      const filtered = items.filter(item => {{
        if (onlyInteractive && !item.is_interactive) return false;
        if (activeCategory !== 'ALL') {{
          const catMatch = item.category.toLowerCase().includes(activeCategory.toLowerCase()) || 
                           item.path_domain.toLowerCase().includes(activeCategory.toLowerCase());
          if (!catMatch) return false;
        }}
        if (activeLevel !== 'ALL') {{
          const lvlMatch = item.target_level.toLowerCase().includes(activeLevel.toLowerCase()) ||
                           item.path_domain.toLowerCase().includes(activeLevel.toLowerCase().replace(/ /g, '_'));
          if (!lvlMatch) return false;
        }}
        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const matchTitle = item.title.toLowerCase().includes(q);
          const matchTopic = item.topic.toLowerCase().includes(q);
          const matchLevel = item.target_level.toLowerCase().includes(q);
          const matchCat = item.category.toLowerCase().includes(q);
          if (!matchTitle && !matchTopic && !matchLevel && !matchCat) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted); background: var(--surface); border-radius: var(--radius); border: 1px dashed var(--border);">No matching resources found. Try adjusting your filters or search terms.</div>';
        return;
      }}

      grid.innerHTML = filtered.map(item => `
        <div class="content-card">
          <div>
            <div class="card-top">
              <span class="cat-badge">${{item.category.replace(/_/g, ' ')}}</span>
              <span class="level-tag">${{item.target_level}}</span>
            </div>
            <h3 class="card-title">${{item.title}}</h3>
            <p class="card-desc">
              <strong>Type:</strong> ${{item.content_type}}<br>
              <strong>Topic:</strong> ${{item.topic}}
            </p>
          </div>
          <div class="card-actions">
            <a href="${{item.link_domain || item.path_domain}}" class="btn-launch ${{item.is_interactive ? 'btn-interactive' : ''}}">
              ${{item.is_interactive ? '🚀 Launch Interactive App' : '📄 View Study Material'}}
            </a>
          </div>
        </div>
      `).join('');
    }}

    function filterCategory(cat) {{
      activeCategory = cat;
      onlyInteractive = false;
      renderGrid();
    }}

    function filterLevel(lvl) {{
      activeLevel = lvl;
      renderGrid();
    }}

    function filterInteractive() {{
      onlyInteractive = !onlyInteractive;
      renderGrid();
    }}

    function handleSearch() {{
      searchQuery = document.getElementById('searchBox').value.trim();
      renderGrid();
    }}

    renderGrid();
  </script>
</body>
</html>
"""


def generate_root_portal_html(items: list):
    items_json = json.dumps(items, ensure_ascii=False, indent=2)
    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>AG Teaching Portal | Educational Content & Exam Simulators</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #f8fafc;
      --surface: #ffffff;
      --card-bg: #ffffff;
      --text: #0f172a;
      --text-muted: #64748b;
      --primary: #3b82f6;
      --primary-hover: #2563eb;
      --primary-light: #eff6ff;
      --border: #e2e8f0;
      --tag-ielts: #ef4444;
      --tag-sat: #8b5cf6;
      --tag-esl: #10b981;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.05), 0 2px 4px -2px rgb(0 0 0 / 0.05);
      --radius: 12px;
      --font: 'Plus Jakarta Sans', system-ui, sans-serif;
      --font-mono: 'JetBrains Mono', monospace;
    }}

    [data-theme="dark"] {{
      --bg: #0b0f19;
      --surface: #131b2e;
      --card-bg: #1e293b;
      --text: #f1f5f9;
      --text-muted: #94a3b8;
      --primary: #60a5fa;
      --primary-hover: #3b82f6;
      --primary-light: #1e293b;
      --border: #334155;
      --shadow: 0 4px 6px -1px rgb(0 0 0 / 0.3);
    }}

    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: var(--font);
      background-color: var(--bg);
      color: var(--text);
      line-height: 1.6;
      padding-bottom: 60px;
    }}

    header {{
      background: var(--surface);
      border-bottom: 1px solid var(--border);
      padding: 1.5rem 2rem;
      position: sticky;
      top: 0;
      z-index: 100;
      box-shadow: var(--shadow);
    }}

    .header-content {{
      max-width: 1240px;
      margin: 0 auto;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .brand {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}

    .brand-icon {{
      background: linear-gradient(135deg, #3b82f6, #8b5cf6);
      color: white;
      font-weight: 800;
      padding: 8px 14px;
      border-radius: 10px;
      font-size: 1.2rem;
    }}

    .brand h1 {{
      font-size: 1.25rem;
      font-weight: 700;
    }}

    .brand p {{
      font-size: 0.85rem;
      color: var(--text-muted);
    }}

    .theme-toggle {{
      background: var(--primary-light);
      color: var(--text);
      border: 1px solid var(--border);
      padding: 8px 14px;
      border-radius: 8px;
      cursor: pointer;
      font-weight: 600;
    }}

    main {{
      max-width: 1240px;
      margin: 2rem auto;
      padding: 0 1.5rem;
    }}

    .hero-banner {{
      background: linear-gradient(135deg, rgba(59, 130, 246, 0.08), rgba(139, 92, 246, 0.08));
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 2.25rem;
      margin-bottom: 2rem;
      text-align: center;
    }}

    .hero-banner h2 {{
      font-size: 1.9rem;
      font-weight: 800;
      margin-bottom: 0.5rem;
    }}

    .hero-banner p {{
      color: var(--text-muted);
      max-width: 700px;
      margin: 0 auto 1.5rem auto;
      font-size: 1rem;
    }}

    /* Standalone Domain Launchpads */
    .domain-launchpads {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
      gap: 1.5rem;
      margin-bottom: 2.5rem;
    }}

    .launchpad-card {{
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s, border-color 0.2s;
      position: relative;
      overflow: hidden;
    }}

    .launchpad-card::before {{
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
    }}

    .card-ielts::before {{ background: #ef4444; }}
    .card-sat::before {{ background: #8b5cf6; }}
    .card-esl::before {{ background: #10b981; }}

    .launchpad-card:hover {{
      transform: translateY(-4px);
      box-shadow: 0 12px 20px -4px rgb(0 0 0 / 0.1);
    }}

    .launchpad-header {{
      display: flex;
      align-items: center;
      gap: 12px;
      margin-bottom: 0.75rem;
    }}

    .launchpad-icon {{
      font-size: 1.5rem;
      width: 42px;
      height: 42px;
      display: flex;
      align-items: center;
      justify-content: center;
      border-radius: 8px;
    }}

    .launchpad-title {{
      font-size: 1.15rem;
      font-weight: 700;
    }}

    .launchpad-desc {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
      line-height: 1.5;
    }}

    .launchpad-btn {{
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 8px;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 700;
      font-size: 0.9rem;
      text-decoration: none;
      color: white;
      transition: opacity 0.2s;
    }}

    .launchpad-btn:hover {{ opacity: 0.9; }}

    .btn-ielts {{ background: #ef4444; }}
    .btn-sat {{ background: #8b5cf6; }}
    .btn-esl {{ background: #10b981; }}

    .section-heading {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 1.25rem;
    }}

    .section-heading h3 {{
      font-size: 1.3rem;
      font-weight: 800;
    }}

    .filter-bar {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 2rem;
      align-items: center;
    }}

    .filter-btn {{
      background: var(--surface);
      border: 1px solid var(--border);
      color: var(--text);
      padding: 8px 16px;
      border-radius: 20px;
      cursor: pointer;
      font-size: 0.9rem;
      font-weight: 600;
      transition: all 0.2s ease;
    }}

    .filter-btn.active {{
      background: var(--primary);
      color: white;
      border-color: var(--primary);
    }}

    .search-input {{
      flex: 1;
      min-width: 250px;
      padding: 10px 16px;
      border-radius: 20px;
      border: 1px solid var(--border);
      background: var(--surface);
      color: var(--text);
      font-family: inherit;
    }}

    .card-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fill, minmax(340px, 1fr));
      gap: 1.5rem;
    }}

    .content-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: var(--radius);
      padding: 1.5rem;
      box-shadow: var(--shadow);
      display: flex;
      flex-direction: column;
      justify-content: space-between;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}

    .content-card:hover {{
      transform: translateY(-3px);
      box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
    }}

    .card-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }}

    .domain-badge {{
      font-size: 0.75rem;
      font-weight: 700;
      padding: 4px 10px;
      border-radius: 6px;
      text-transform: uppercase;
    }}

    .domain-IELTS {{ background: #fee2e2; color: #dc2626; }}
    .domain-SAT {{ background: #ede9fe; color: #7c3aed; }}
    .domain-ESL {{ background: #dcfce7; color: #16a34a; }}
    .domain-General {{ background: #e2e8f0; color: #475569; }}

    .level-badge {{
      font-size: 0.75rem;
      font-family: var(--font-mono);
      color: var(--text-muted);
    }}

    .card-title {{
      font-size: 1.15rem;
      font-weight: 700;
      margin-bottom: 0.5rem;
      line-height: 1.4;
    }}

    .card-meta {{
      font-size: 0.85rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }}

    .card-actions {{
      display: flex;
      gap: 10px;
    }}

    .btn-launch {{
      flex: 1;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      padding: 10px 16px;
      border-radius: 8px;
      font-weight: 600;
      text-decoration: none;
      background: var(--primary);
      color: white;
      transition: background 0.2s;
    }}

    .btn-launch:hover {{
      background: var(--primary-hover);
    }}

    .btn-interactive {{
      background: linear-gradient(135deg, #10b981, #059669);
    }}
  </style>
</head>
<body>

  <header>
    <div class="header-content">
      <div class="brand">
        <div class="brand-icon">AG</div>
        <div>
          <h1>AG Teaching & Exam Prep Hub</h1>
          <p>ESL • IELTS Academic • Digital SAT</p>
        </div>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
      <a href="{SITE_REPO_URL}" target="_blank" rel="noopener noreferrer" class="theme-toggle" style="text-decoration:none;">⭐ GitHub Repo</a>
      <button class="theme-toggle" id="themeToggle" onclick="toggleTheme()">🌓 Theme</button>
      </div>
    </div>
  </header>

  <main>
    <div class="hero-banner">
      <h2>Master Curriculum & Interactive Exam Center</h2>
      <p>Select an independent domain portal below or search across all verified lesson plans, high-yield discrete drills, and client-side exam simulators.</p>
    </div>

    <!-- Independent Domain Portals Launchpad -->
    <div class="section-heading">
      <h3>🚀 Independent Domain Portals</h3>
    </div>
    <div class="domain-launchpads">
      <div class="launchpad-card card-ielts">
        <div>
          <div class="launchpad-header">
            <span class="launchpad-icon" style="background: #fee2e2; color: #dc2626;">🎯</span>
            <div>
              <div class="launchpad-title">IELTS Academic</div>
              <div style="font-size: 0.75rem; color: #ef4444; font-weight: 700;">Band 5.0 → 9.0</div>
            </div>
          </div>
          <p class="launchpad-desc">Academic Reading masterclasses, Writing Task 1 interactive packs, Speaking mocks & scoring criteria.</p>
        </div>
        <a href="IELTS/index.html" class="launchpad-btn btn-ielts">
          Open IELTS Portal ➔
        </a>
      </div>

      <div class="launchpad-card card-sat">
        <div>
          <div class="launchpad-header">
            <span class="launchpad-icon" style="background: #ede9fe; color: #7c3aed;">🏛️</span>
            <div>
              <div class="launchpad-title">Digital SAT</div>
              <div style="font-size: 0.75rem; color: #8b5cf6; font-weight: 700;">College Board Blueprint</div>
            </div>
          </div>
          <p class="launchpad-desc">Reading & Writing item sets, Math domain problem banks, adaptive practice modules & Desmos guides.</p>
        </div>
        <a href="SAT/index.html" class="launchpad-btn btn-sat">
          Open SAT Portal ➔
        </a>
      </div>

      <div class="launchpad-card card-esl">
        <div>
          <div class="launchpad-header">
            <span class="launchpad-icon" style="background: #dcfce7; color: #16a34a;">🌍</span>
            <div>
              <div class="launchpad-title">ESL Curriculum</div>
              <div style="font-size: 0.75rem; color: #16a34a; font-weight: 700;">CEFR A1 to C2</div>
            </div>
          </div>
          <p class="launchpad-desc">PPP lesson plans, Task-Based Language Teaching (TBLT) labs, speaking simulators & communicative activities.</p>
        </div>
        <a href="ESL/index.html" class="launchpad-btn btn-esl">
          Open ESL Portal ➔
        </a>
      </div>
    </div>

    <!-- All Workspace Resources -->
    <div class="section-heading">
      <h3>📑 All Workspace Resources & Simulators</h3>
    </div>

    <div class="filter-bar">
      <button class="filter-btn active" onclick="filterDomain('ALL')">All Modules</button>
      <button class="filter-btn" onclick="filterDomain('IELTS')">IELTS Academic</button>
      <button class="filter-btn" onclick="filterDomain('SAT')">Digital SAT</button>
      <button class="filter-btn" onclick="filterDomain('ESL')">ESL</button>
      <button class="filter-btn" onclick="filterInteractive()">🚀 Interactive Simulators</button>
      <input type="text" class="search-input" id="searchBox" placeholder="🔍 Search topics, skills, or titles across entire workspace..." oninput="handleSearch()">
    </div>

    <div class="card-grid" id="contentGrid">
      <!-- Injected by JS -->
    </div>
  </main>

  <script>
    const items = {items_json};

    let activeFilter = 'ALL';
    let onlyInteractive = false;
    let searchQuery = '';

    function toggleTheme() {{
      const html = document.documentElement;
      const current = html.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      html.setAttribute('data-theme', next);
      localStorage.setItem('ag_theme', next);
    }}

    const savedTheme = localStorage.getItem('ag_theme');
    if (savedTheme) {{
      document.documentElement.setAttribute('data-theme', savedTheme);
    }}

    function renderGrid() {{
      const grid = document.getElementById('contentGrid');
      const filtered = items.filter(item => {{
        if (onlyInteractive && !item.is_interactive) return false;
        if (activeFilter !== 'ALL' && item.domain !== activeFilter) return false;
        if (searchQuery) {{
          const q = searchQuery.toLowerCase();
          const matchTitle = item.title.toLowerCase().includes(q);
          const matchTopic = item.topic.toLowerCase().includes(q);
          const matchLevel = item.target_level.toLowerCase().includes(q);
          if (!matchTitle && !matchTopic && !matchLevel) return false;
        }}
        return true;
      }});

      if (filtered.length === 0) {{
        grid.innerHTML = '<div style="grid-column: 1/-1; text-align: center; padding: 3rem; color: var(--text-muted); background: var(--surface); border-radius: var(--radius);">No matching resources found.</div>';
        return;
      }}

      grid.innerHTML = filtered.map(item => `
        <div class="content-card">
          <div>
            <div class="card-header">
              <span class="domain-badge domain-${{item.domain}}">${{item.domain}}</span>
              <span class="level-badge">${{item.target_level}}</span>
            </div>
            <h3 class="card-title">${{item.title}}</h3>
            <p class="card-meta">
              <strong>Type:</strong> ${{item.content_type}}<br>
              <strong>Topic:</strong> ${{item.topic}}
            </p>
          </div>
          <div class="card-actions">
            <a href="${{item.link_root || item.path_root}}" class="btn-launch ${{item.is_interactive ? 'btn-interactive' : ''}}">
              ${{item.is_interactive ? '🚀 Launch Simulator' : '📄 Open Document'}}
            </a>
          </div>
        </div>
      `).join('');
    }}

    function filterDomain(dom) {{
      activeFilter = dom;
      onlyInteractive = false;
      updateFilterButtons();
      renderGrid();
    }}

    function filterInteractive() {{
      onlyInteractive = !onlyInteractive;
      updateFilterButtons();
      renderGrid();
    }}

    function updateFilterButtons() {{
      document.querySelectorAll('.filter-btn').forEach(btn => {{
        btn.classList.remove('active');
        if (!onlyInteractive && btn.innerText.includes(activeFilter)) {{
          btn.classList.add('active');
        }} else if (onlyInteractive && btn.innerText.includes('Interactive')) {{
          btn.classList.add('active');
        }} else if (!onlyInteractive && activeFilter === 'ALL' && btn.innerText.includes('All')) {{
          btn.classList.add('active');
        }}
      }});
    }}

    function handleSearch() {{
      searchQuery = document.getElementById('searchBox').value.trim();
      renderGrid();
    }}

    renderGrid();
  </script>
</body>
</html>
"""


def generate_markdown_index(items):
    out = [
        "# 📚 Master Workspace Educational Content Catalog",
        "",
        f"> *Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} via `scripts/build_workspace_index.py`*",
        "",
        "This catalog indexes all structured lesson plans, test prep modules, question banks, and interactive simulators across the workspace, along with independent domain portals.",
        "",
        "---",
        "",
        "## 🚀 Dedicated Domain Portals",
        "",
        "- 🎯 **IELTS Academic Portal**: [`IELTS/index.html`](IELTS/index.html) *(Repo: [mikefai/AG-IELTS-Academic](https://github.com/mikefai/AG-IELTS-Academic))*",
        "- 🏛️ **Digital SAT Portal**: [`SAT/index.html`](SAT/index.html) *(Repo: [mikefai/AG-SAT](https://github.com/mikefai/AG-SAT))*",
        "- 🌍 **ESL Curriculum Portal**: [`ESL/index.html`](ESL/index.html)",
        "",
        "---",
        ""
    ]

    for domain in DOMAINS:
        domain_items = [it for it in items if it["domain"].upper() == domain]
        out.append(f"## 🌐 {domain} Modules & Resources ({len(domain_items)} Total)")
        out.append("")
        if not domain_items:
            out.append(f"*No content files currently created in `{domain}/`.*")
            out.append("")
            continue

        out.append("| Type | Title / Topic | Target Level | Format | Direct Link |")
        out.append("| :--- | :--- | :--- | :--- | :--- |")
        for it in sorted(domain_items, key=lambda x: (x["content_type"], x["title"])):
            fmt = "🚀 **Interactive App**" if it["is_interactive"] else "📄 Markdown"
            out.append(f"| {it['content_type']} | {it['topic']} | `{it['target_level']}` | {fmt} | [{it['title']}]({it['path_root']}) |")
        out.append("")

    return "\n".join(out)


def main():
    print("Scanning workspace items...")
    items = scan_workspace()
    print(f"Found {len(items)} content items ({sum(1 for i in items if i['is_interactive'])} interactive).")

    # 1. Generate Domain-specific Portals
    for domain in DOMAINS:
        domain_dir = WORKSPACE_ROOT / domain
        if domain_dir.exists():
            portal_html = generate_domain_portal_html(domain, items)
            portal_path = domain_dir / "index.html"
            portal_path.write_text(portal_html, encoding="utf-8")
            print(f"Generated {domain} dedicated portal: {portal_path.relative_to(WORKSPACE_ROOT)}")

    # 2. Generate Master Markdown Index
    md_index = generate_markdown_index(items)
    (WORKSPACE_ROOT / "WORKSPACE_INDEX.md").write_text(md_index, encoding="utf-8")
    print("Updated WORKSPACE_INDEX.md")

    # 3. Generate Master Root Portal HTML
    root_portal_html = generate_root_portal_html(items)
    (WORKSPACE_ROOT / "index.html").write_text(root_portal_html, encoding="utf-8")
    print("Updated root index.html master portal.")


if __name__ == "__main__":
    main()
