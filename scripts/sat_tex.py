#!/usr/bin/env python3
"""LaTeX-subset to HTML + markdown-lite helpers for the SAT compiler.

Handles the exact subset used across SAT/*.md: fractions, roots, sup/sub,
cases, Greek, operators, \\text{}, spacing and delimiters.
"""

import html
import re

SYMBOLS = {
    "cdot": "·", "times": "×", "div": "÷", "pm": "±", "mp": "∓",
    "leq": "≤", "geq": "≥", "neq": "≠", "approx": "≈", "equiv": "≡",
    "cong": "≅", "Delta": "Δ", "delta": "δ", "pi": "π", "theta": "θ",
    "lambda": "λ", "mu": "μ", "sigma": "σ", "alpha": "α", "beta": "β",
    "infty": "∞", "circ": "∘", "ldots": "…", "cdots": "⋯", "vdots": "⋮",
    "mid": "|", "parallel": "∥", "perp": "⊥", "angle": "∠", "triangle": "△",
    "sim": "~", "propto": "∝", "forall": "∀", "exists": "∃", "in": "∈",
    "cup": "∪", "cap": "∩", "subset": "⊂", "surd": "√",
    "leftarrow": "←", "rightarrow": "→", "Rightarrow": "⇒", "implies": "⇒",
    "leqq": "≤", "geqq": "≥",
}


def _brace_arg(s, i):
    """s[i] == '{' -> (content, index_after_closing). Handles nesting."""
    assert s[i] == "{"
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def tex_to_html(math):
    """Convert a LaTeX math string (no $ delimiters) to HTML."""
    # spacing / punctuation pre-pass
    math = math.replace("{,}", ",")
    math = re.sub(r"\\[,;:]", " ", math)
    math = math.replace("\\!", "")
    # cases environment first (contains \\ separators); shield its HTML from
    # the escaping character loop below via placeholders.
    kept = []

    def _cases(m):
        inner = m.group(1)
        rows = [r.strip() for r in inner.split("\\\\")]
        cells = []
        for r in rows:
            parts = [c.strip() for c in r.split("&")]
            cells.append("<span>" + "</span><span>".join(tex_to_html(p) for p in parts) + "</span>")
        idx = len(kept)
        kept.append('<span class="mx-cases"><span class="mx-brace">\u23a7</span><span class="mx-rows">' + "".join(
            f'<span class="mx-row">{c}</span>' for c in cells) + "</span></span>")
        return f"\x00K{idx}\x00"

    math = re.sub(r"\\begin\{cases\}(.*?)\\end\{cases\}", _cases, math, flags=re.S)

    out, i = [], 0
    n = len(math)
    while i < n:
        c = math[i]
        if c == "\\":
            m = re.match(r"\\([a-zA-Z]+)", math[i:])
            if m:
                cmd = m.group(1)
                j = i + 1 + len(cmd)
                if cmd in ("frac", "dfrac", "tfrac"):
                    a, j = _brace_arg(math, j) if j < n and math[j] == "{" else ("?", j)
                    b, j = _brace_arg(math, j) if j < n and math[j] == "{" else ("?", j)
                    out.append(f'<span class="mx-frac"><span>{tex_to_html(a)}</span><span>{tex_to_html(b)}</span></span>')
                    i = j
                    continue
                if cmd == "sqrt":
                    idx = ""
                    if j < n and math[j] == "[":
                        k = math.find("]", j)
                        idx = math[j + 1:k]
                        j = k + 1
                    a, j = _brace_arg(math, j) if j < n and math[j] == "{" else ("?", j)
                    sup = f"<sup>{html.escape(idx)}</sup>" if idx else ""
                    out.append(f"√{sup}<span class=\"mx-root\">{tex_to_html(a)}</span>")
                    i = j
                    continue
                if cmd == "text":
                    a, j = _brace_arg(math, j) if j < n and math[j] == "{" else ("", j)
                    out.append(html.escape(a))
                    i = j
                    continue
                if cmd in ("left", "right"):
                    i = j
                    if j < n and math[j] in "()[]{}|.":
                        i = j + 1
                    continue
                if cmd in (" ", ",", ";", ":", "!", "quad", "qquad"):
                    out.append(" " if cmd in (" ", ",", ":", ";", "quad", "qquad") else "")
                    i = j
                    continue
                if cmd in SYMBOLS:
                    out.append(SYMBOLS[cmd])
                    i = j
                    continue
                # unknown command: keep readable text
                out.append(cmd)
                i = j
                continue
            # escaped single char: \%, \$, \{, \}, \&, \#, \_
            if i + 1 < n:
                out.append(html.escape(math[i + 1]))
                i += 2
                continue
            i += 1
            continue
        if c == "^":
            if i + 1 < n and math[i + 1] == "{":
                a, j = _brace_arg(math, i + 1)
                out.append(f"<sup>{tex_to_html(a)}</sup>")
                i = j
            elif i + 1 < n:
                out.append(f"<sup>{html.escape(math[i + 1])}</sup>")
                i += 2
            else:
                i += 1
            continue
        if c == "_":
            if i + 1 < n and math[i + 1] == "{":
                a, j = _brace_arg(math, i + 1)
                out.append(f"<sub>{tex_to_html(a)}</sub>")
                i = j
            elif i + 1 < n:
                out.append(f"<sub>{html.escape(math[i + 1])}</sub>")
                i += 2
            else:
                i += 1
            continue
        if c == "&":
            out.append(" ")
        elif c == "~":
            out.append("&nbsp;")
        else:
            out.append(html.escape(c))
        i += 1
    res = "".join(out)
    for idx, span in enumerate(kept):
        res = res.replace(f"\x00K{idx}\x00", span)
    return res


def _unescaped_dollars(s):
    """Positions of $ not preceded by a backslash."""
    return [m.start() for m in re.finditer(r"\$", s)
            if not (m.start() > 0 and s[m.start() - 1] == "\\")]


def _render_math_spans(s):
    """Replace $$..$$ and $..$ spans with rendered HTML.

    Delimiters pair left-to-right (display first, then inline); a trailing
    unmatched $ is left as literal text.
    """
    # display math: pair up $$ delimiters
    dd = _unescaped_dollars(s)
    disp = []
    i = 0
    while i + 1 < len(dd):
        if dd[i] + 1 == dd[i + 1]:  # $$ opener
            j = i + 2
            while j + 1 < len(dd) and not (dd[j] + 1 == dd[j + 1]):
                j += 1
            if j + 1 < len(dd):
                disp.append((dd[i], dd[j]))  # (opener $, closer $)
                i = j + 2
                continue
        i += 1
    parts = []
    if disp:
        chunks, prev = [], 0
        for a, b in disp:
            chunks.append(s[prev:a])
            idx = len(parts)
            parts.append(("D", tex_to_html(s[a + 2:b])))
            chunks.append(f"\x00{idx}\x00")
            prev = b + 2
        chunks.append(s[prev:])
        s = "".join(chunks)
    # inline math: pair remaining single $ left-to-right
    poss = _unescaped_dollars(s)
    if len(poss) >= 2:
        chunks, prev = [], 0
        for k in range(0, len(poss) - 1, 2):
            a, b = poss[k], poss[k + 1]
            chunks.append(s[prev:a])
            idx = len(parts)
            parts.append(("I", tex_to_html(s[a + 1:b])))
            chunks.append(f"\x00{idx}\x00")
            prev = b + 1
        chunks.append(s[prev:])
        s = "".join(chunks)
    # escape everything, then restore math spans
    s = html.escape(s)
    for idx, (kind, inner) in enumerate(parts):
        cls = "mx-disp" if kind == "D" else "mx"
        s = s.replace(f"\x00{idx}\x00", f'<span class="{cls}">{inner}</span>')
    return s


def md_inline(s):
    """Inline markdown (-> HTML): code, bold, italic, links, then math."""
    code = []

    def _sub_code(m):
        idx = len(code)
        code.append(f"<code>{html.escape(m.group(1))}</code>")
        return f"\x00C{idx}\x00"
    s = re.sub(r"`([^`]+?)`", _sub_code, s)
    s = _render_math_spans(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<!\*)\*([^*\n]+?)\*(?!\*)", r"<em>\1</em>", s)
    s = re.sub(r"\[([^\]]+?)\]\(([^)]+?)\)", r'<a href="\2">\1</a>', s)
    for idx, span in enumerate(code):
        s = s.replace(f"\x00C{idx}\x00", span)
    s = s.replace("\\$", "$").replace("\\%", "%").replace("\\&", "&amp;")
    return s


def md_blocks(s):
    """Block markdown (-> HTML): headers, lists, tables, hr, paragraphs."""
    lines = s.split("\n")
    out, i, para = [], 0, []
    def flush_para():
        if para:
            out.append("<p>" + md_inline(" ".join(para)) + "</p>")
            para.clear()
    while i < len(lines):
        line = lines[i].rstrip()
        if not line.strip():
            flush_para()
            i += 1
            continue
        m = re.match(r"^(#{1,4})\s+(.*)$", line)
        if m:
            flush_para()
            lvl = min(len(m.group(1)) + 1, 4)
            out.append(f"<h{lvl}>{md_inline(m.group(2))}</h{lvl}>")
            i += 1
            continue
        if re.match(r"^\s*---+\s*$", line):
            flush_para()
            out.append("<hr>")
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", line):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append("<li>" + md_inline(re.sub(r"^\s*[-*]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        if re.match(r"^\s*\d+[.)]\s+", line):
            flush_para()
            items = []
            while i < len(lines) and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append("<li>" + md_inline(re.sub(r"^\s*\d+[.)]\s+", "", lines[i])) + "</li>")
                i += 1
            out.append("<ol>" + "".join(items) + "</ol>")
            continue
        if "|" in line and i + 1 < len(lines) and re.match(r"^\s*\|?[\s:|-]+\|?\s*$", lines[i + 1]):
            flush_para()
            header = [c.strip() for c in line.strip().strip("|").split("|")]
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append([c.strip() for c in lines[i].strip().strip("|").split("|")])
                i += 1
            t = ["<table><thead><tr>" + "".join(f"<th>{md_inline(c)}</th>" for c in header) + "</tr></thead><tbody>"]
            for r in rows:
                t.append("<tr>" + "".join(f"<td>{md_inline(c)}</td>" for c in r) + "</tr>")
            t.append("</tbody></table>")
            out.append("".join(t))
            continue
        if line.lstrip().startswith(">"):
            flush_para()
            qs = []
            while i < len(lines) and lines[i].lstrip().startswith(">"):
                qs.append(lines[i].lstrip()[1:].strip())
                i += 1
            out.append("<blockquote>" + md_inline(" ".join(qs)) + "</blockquote>")
            continue
        para.append(line.strip())
        i += 1
    flush_para()
    return "\n".join(out)
