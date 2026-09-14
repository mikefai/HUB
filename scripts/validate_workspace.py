#!/usr/bin/env python3
"""
Workspace Educational Content Validator
Audits markdown files across ESL, IELTS, and SAT for YAML metadata,
folder routing consistency, answer keys, and pedagogical standards.
"""

import os
import sys
import re
from pathlib import Path

# Ensure UTF-8 stdout on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# ANSI Colors for terminal output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DOMAINS = {"ESL", "IELTS", "SAT"}
EXCLUDED_FILENAMES = {"README.md", "AGENTS.md", "GEMINI.md", "WORKSPACE_INDEX.md", "routing.md"}

REQUIRED_METADATA_FIELDS = ["domain", "target_level", "topic", "date_created", "content_type"]


def extract_frontmatter(content: str):
    """Extracts YAML frontmatter as a dict from markdown text."""
    if not content.startswith("---"):
        return None, "Missing YAML frontmatter opening '---'"
    
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None, "Unclosed YAML frontmatter delimiter"
    
    yaml_text = parts[1]
    metadata = {}
    for line in yaml_text.strip().split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            metadata[key] = val
            
    return metadata, None


def validate_file(file_path: Path):
    """Validates a single educational content markdown file."""
    rel_path = file_path.relative_to(WORKSPACE_ROOT)
    errors = []
    warnings = []

    try:
        content = file_path.read_text(encoding="utf-8")
    except Exception as e:
        return [f"Unable to read file: {e}"], []

    # Check if in Templates
    is_template = "Templates" in file_path.parts

    # 1. Frontmatter check
    metadata, err = extract_frontmatter(content)
    if err:
        errors.append(err)
        return errors, warnings

    for req_key in REQUIRED_METADATA_FIELDS:
        if req_key not in metadata or not metadata[req_key]:
            if not is_template:
                errors.append(f"Missing required metadata key: '{req_key}'")

    if not is_template:
        domain = metadata.get("domain", "").upper()
        if domain not in DOMAINS:
            warnings.append(f"Declared domain '{domain}' is not one of {sorted(DOMAINS)}")
        
        # Check folder routing
        top_folder = rel_path.parts[0].upper()
        if top_folder in DOMAINS and domain and domain != top_folder:
            errors.append(f"Folder mismatch: File is in '{top_folder}/' but metadata declares domain: '{domain}'")

    # 2. Check for Answer Key if content is Quiz/Test/Drill/Reading (excluding Speaking/Writing performance tasks)
    content_type = metadata.get("content_type", "").lower()
    is_mcq_assessment = any(kw in content_type for kw in ["quiz", "drill", "question", "reading", "practice"]) and not any(kw in content_type for kw in ["speaking", "writing", "essay", "lesson plan"])
    
    if is_mcq_assessment and not is_template:
        has_answer_key = bool(re.search(r"(?:##|###)\s*(?:[^\n]*\b(?:Answer Key|Answers|Cevap Anahtarı|Çözümler)\b)", content, re.I))
        if not has_answer_key:
            warnings.append("Assessment content type detected, but no 'Answer Key' or 'Cevap Anahtarı' section found")

        has_rationale = bool(re.search(r"(?:Distractor|Rationale|Explanation|Açıklama|Çeldirici)", content, re.I))
        if not has_rationale:
            warnings.append("No distractor analysis or solution rationale detected")

    return errors, warnings


def main():
    print(f"\n{BOLD}{CYAN}======================================================{RESET}")
    print(f"{BOLD}{CYAN}   [+] Workspace Educational Content Validator        {RESET}")
    print(f"{BOLD}{CYAN}======================================================{RESET}\n")

    files_to_check = []
    for search_dir in ["ESL", "IELTS", "SAT", "Templates"]:
        dir_path = WORKSPACE_ROOT / search_dir
        if dir_path.exists():
            for p in dir_path.rglob("*.md"):
                if p.name not in EXCLUDED_FILENAMES:
                    files_to_check.append(p)

    total_files = len(files_to_check)
    passed_count = 0
    warning_count = 0
    error_count = 0

    for file_path in sorted(files_to_check):
        rel_path = file_path.relative_to(WORKSPACE_ROOT)
        errors, warnings = validate_file(file_path)

        if errors:
            error_count += 1
            print(f"{RED}[FAIL]{RESET} {BOLD}{rel_path}{RESET}")
            for err in errors:
                print(f"        {RED}* {err}{RESET}")
            for wrn in warnings:
                print(f"        {YELLOW}^ {wrn}{RESET}")
        elif warnings:
            warning_count += 1
            print(f"{YELLOW}[WARN]{RESET} {BOLD}{rel_path}{RESET}")
            for wrn in warnings:
                print(f"        {YELLOW}* {wrn}{RESET}")
        else:
            passed_count += 1
            print(f"{GREEN}[PASS]{RESET} {rel_path}")

    print(f"\n{BOLD}Audit Summary:{RESET}")
    print(f"  Total Scanned: {total_files}")
    print(f"  {GREEN}Passed:{RESET}        {passed_count}")
    print(f"  {YELLOW}Warnings:{RESET}      {warning_count}")
    print(f"  {RED}Errors:{RESET}        {error_count}\n")

    if error_count > 0:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
