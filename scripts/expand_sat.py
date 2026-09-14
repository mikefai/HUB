#!/usr/bin/env python3
"""Append expansion fragments (questions + key rows + rationales) to SAT drill MDs.

Fragment file format (scripts/frag_<name>.md):
    @@QUESTIONS@@
    <###/## Question blocks, each ending with --->
    @@KEYS@@
    <| **QN** | ... | table rows>
    @@RAT@@
    <###/#### Question N rationale sections>
    @@OVERVIEW@@
    <full replacement line for '- **Number of Items**: ...'>
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent
FRAG = Path(__file__).parent

JOBS = [
    ("SAT/Math/Algebra/sat_math_algebra_and_advanced_functions_set_01.md", "frag_algebra.md"),
    ("SAT/Math/Advanced_Math/sat_math_advanced_math_polynomials_and_nonlinear_systems_set_02.md", "frag_advmath.md"),
    ("SAT/Math/Geometry_and_Trigonometry/sat_math_geometry_trigonometry_and_data_set_01.md", "frag_geo.md"),
    ("SAT/Math/Problem_Solving_and_Data_Analysis/sat_math_problem_solving_data_statistics_set_01.md", "frag_prob.md"),
    ("SAT/Reading_Writing/Craft_and_Structure/sat_craft_and_structure_cross_text_connections_set_02.md", "frag_cross.md"),
    ("SAT/Reading_Writing/Craft_and_Structure/sat_craft_and_structure_words_in_context_set_01.md", "frag_words.md"),
    ("SAT/Reading_Writing/Expression_of_Ideas/sat_expression_of_ideas_transitions_rhetorical_synthesis_set_01.md", "frag_trans.md"),
    ("SAT/Reading_Writing/Information_and_Ideas/sat_information_and_ideas_evidence_inference_set_01.md", "frag_evid.md"),
    ("SAT/Reading_Writing/Information_and_Ideas/sat_information_and_ideas_scientific_tables_and_graphs_set_02.md", "frag_tables.md"),
    ("SAT/Reading_Writing/Standard_English_Conventions/sat_standard_english_conventions_boundaries_and_modifiers_set_01.md", "frag_bound.md"),
    ("SAT/Reading_Writing/Standard_English_Conventions/sat_standard_english_conventions_verbs_pronouns_parallelism_set_02.md", "frag_verbs.md"),
]


def split_frag(text):
    parts = {}
    cur, buf = None, []
    for line in text.split("\n"):
        if line.strip() in ("@@QUESTIONS@@", "@@KEYS@@", "@@RAT@@", "@@OVERVIEW@@"):
            if cur:
                parts[cur] = "\n".join(buf).strip() + "\n"
            cur = line.strip().strip("@")
            buf = []
        else:
            buf.append(line)
    if cur:
        parts[cur] = "\n".join(buf).strip() + "\n"
    return parts


def main():
    for rel, frag_name in JOBS:
        md_path = ROOT / rel
        frag_path = FRAG / frag_name
        if not frag_path.exists():
            print(f"[SKIP] {rel} (no {frag_name})")
            continue
        text = md_path.read_text(encoding="utf-8")
        parts = split_frag(frag_path.read_text(encoding="utf-8"))
        # 1. questions before the answer-key header
        m = re.search(r"^##\s+[^\n]*Answer Key[^\n]*$", text, re.M)
        assert m, f"{rel}: answer-key header not found"
        text = text[:m.start()] + parts["QUESTIONS"] + "\n" + text[m.start():]
        # 2. key rows after the last key-table row
        rows = list(re.finditer(r"^\|\s*\*\*Q\d+\*\*.*$", text, re.M))
        assert rows, f"{rel}: no key rows"
        last = rows[-1]
        text = text[:last.end()] + "\n" + parts["KEYS"].rstrip("\n") + text[last.end():]
        # 3. rationales before the alignment footer
        m2 = re.search(r"^##\s+New System Alignment", text, re.M)
        assert m2, f"{rel}: alignment footer not found"
        text = text[:m2.start()] + parts["RAT"] + "\n" + text[m2.start():]
        # 4. overview count line
        m3 = re.search(r"^-\s+\*\*Number of Items\*\*:.*$", text, re.M)
        assert m3, f"{rel}: overview line not found"
        text = text[:m3.start()] + parts["OVERVIEW"].rstrip("\n") + text[m3.end():]
        md_path.write_text(text, encoding="utf-8")
        print(f"[EXPANDED] {rel}")


if __name__ == "__main__":
    main()
