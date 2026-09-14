#!/usr/bin/env python3
"""Rebalance answer keys in SAT Skills drills.

Each drill has 3 questions; the generator left all three with the same key
(AAA or BBB). For each file this swaps option *contents* between two letter
slots (Q2 and Q3) and remaps the letters inside that question's rationale, so
keys spread across the options. Verified by hand per file before coding.

Usage: python scripts/fix_skill_keys.py  (then re-run key audit + node check)
"""

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent.parent

# file -> list of (question_no, letter_a, letter_b): swap contents of the two
# slots; the correct answer (currently at letter_a) moves to letter_b.
PLAN = {
    # DONE (verified B,C,D / A,C,D spreads): advanced_math, algebra, craft,
    # geometry. Kept out so reruns refuse via the key assertion.
    "SAT/Skills/information_ideas_skill.html": [(2, "B", "C"), (3, "B", "A")],
    "SAT/Skills/standard_conventions_skill.html": [(2, "B", "C"), (3, "B", "D")],
}

SQ = r"'(?:[^'\\]|\\.)*'"  # single-quoted JS string
DQ = r'"(?:[^"\\]|\\.)*"'  # double-quoted JS string


def swap_letters(text, x, y):
    tmp = "\x00"
    text = re.sub(r"\b" + x + r"\b", tmp, text)
    text = re.sub(r"\b" + y + r"\b", x, text)
    return text.replace(tmp, y)


def swap_options(chunk, q, la, lb, new_key):
    """Swap inner contents of option buttons la/lb; set all onclick keys."""
    btns = list(re.finditer(r'(<button class="opt" onclick="pick\(this,' + str(q) + r",'([A-D])'\)\">)([A-D]\))(.*?)(</button>)", chunk))
    assert len(btns) == 4, f"Q{q}: found {len(btns)} buttons"
    # groups: 1=tag+onclick, 2=key letter, 3=visible label like "B)", 4=content, 5=close
    labels = [m.group(3)[0] for m in btns]
    assert labels == ["A", "B", "C", "D"], f"Q{q}: labels {labels}"
    contents = {m.group(3)[0]: m.group(4) for m in btns}
    contents[la], contents[lb] = contents[lb], contents[la]
    out = chunk
    for m in reversed(btns):
        lab = m.group(3)[0]
        new_tag = re.sub(r"pick\(this," + str(q) + r",'([A-D])'\)",
                         f"pick(this,{q},'{new_key}')", m.group(1))
        out = out[:m.start()] + new_tag + m.group(3) + contents[lab] + m.group(5) + out[m.end():]
    return out


def fix_type_a(text, q, la, lb):
    """QD-map files: {"q": {"key": "K", "rat": "RAT", ...}}"""
    pat = re.compile(r'"%d": \{"key": "([A-D])", "rat": (%s)' % (q, DQ))
    m = pat.search(text)
    assert m, f"Q{q}: QD entry not found"
    assert m.group(1) == la, f"Q{q}: key is {m.group(1)}, expected {la}"
    rat = m.group(2)
    inner = rat[1:-1]
    new_rat = '"' + swap_letters(inner, la, lb) + '"'
    return text[:m.start(1)] + lb + text[m.end(1):m.start(2)] + new_rat + text[m.end(2):]


def fix_type_b(text, q, la, lb):
    """Inline files use a nested ternary per feedback line:
    (q===1?'Q1…':q===2?'Q2…':'Q3…') — one on the Correct line, one on the
    Incorrect line. Swap letters inside the Qn strings only."""
    pat = re.compile(r'q===1\?(%s):q===2\?(%s):(%s)' % (SQ, SQ, SQ))
    found = list(pat.finditer(text))
    assert len(found) == 2, f"Q{q}: found {len(found)} nested ternaries"
    out = text
    for m in reversed(found):
        s = m.group(q)  # groups 1..3 map to Q1..Q3
        out = out[:m.start(q)] + "'" + swap_letters(s[1:-1], la, lb) + "'" + out[m.end(q):]
    return out


def q_chunk(text, q):
    start = text.index(f'<div class="q" id="q{q}">')
    fb = text.index(f'<div id="fb{q}"', start)
    end1 = text.index('</div>', fb) + len('</div>')   # closes fb div
    end2 = text.index('</div>', end1) + len('</div>')  # closes q div
    return start, end2


def main():
    for rel, swaps in PLAN.items():
        p = ROOT / rel
        text = p.read_text(encoding="utf-8")
        is_a = "const QD =" in text
        for q, la, lb in swaps:
            s, e = q_chunk(text, q)
            chunk = text[s:e]
            # sanity: current key really is la on all 4 buttons
            keys = set(re.findall(r"pick\(this," + str(q) + r",'([A-D])'\)", chunk))
            assert keys == {la}, f"{rel} Q{q}: keys {keys}, expected {{{la}}}"
            text = text[:s] + swap_options(chunk, q, la, lb, lb) + text[e:]
            if is_a:
                text = fix_type_a(text, q, la, lb)
            else:
                text = fix_type_b(text, q, la, lb)
        p.write_text(text, encoding="utf-8")
        print(f"[FIXED] {rel}")


if __name__ == "__main__":
    main()
