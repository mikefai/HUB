#!/usr/bin/env python3
"""SAT interactive simulator builder (from scratch).

Parses SAT/*.md drill sources (math-domain, RW-domain, 35-item banks,
practice modules) and rebuilds each .html twin as a TRUE interactive
simulator: practice/exam modes, countdown, progress, flagging, pills,
instant rationales, SPR inputs, keyboard, dark mode, print, portal crumbs,
B1 vocab + student-tools toolbar baked in.

Usage:
    python scripts/build_sat_interactive.py --all     # rebuild every SAT drill twin
    python scripts/build_sat_interactive.py <md...>   # rebuild listed sources
    python scripts/build_sat_interactive.py --check   # parse + report only
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))
from sat_tex import md_inline, md_blocks  # noqa: E402

try:
    from student_tools import build_snippet as _st_snippet
except Exception:
    _st_snippet = None

WORKSPACE_ROOT = HERE.parent

OPT_RE = re.compile(r"^\s*[-*]\s+\*{0,2}([A-E])[).]\*{0,2}\s+(.*)$", re.M)
QHEAD_RE = re.compile(r"^#{2,4}\s+(?:Question\s+(\d+)|Q(\d+))\b[ \t]*(.*)$", re.M)
KEYROW_RE = re.compile(r"^\|\s*\*\*Q?(\d+)\*\*\s*\|\s*(.+?)\s*\|(.*)$", re.M)
INLINE_ANS_RE = re.compile(r"^\*\*Answer:\*\*\s*([A-E])\.\s*(.*)$", re.M | re.S)


def frontmatter(text):
    meta, body = {}, text
    if text.startswith("---"):
        parts = text.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    k, v = line.split(":", 1)
                    meta[k.strip()] = v.strip().strip('"').strip("'")
            body = parts[2]
    return meta, body


def clean_title(t):
    return re.sub(r"^[^\w\s]+", "", t).strip()


def split_questions(body):
    """Yield (num, header_rest, block_text) for each ### Question N block."""
    matches = list(QHEAD_RE.finditer(body))
    out = []
    for i, m in enumerate(matches):
        num = int(m.group(1) or m.group(2))
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out.append((num, (m.group(3) or "").strip(), body[m.end():end]))
    return out


def parse_options(block):
    opts = []
    for m in OPT_RE.finditer(block):
        opts.append({"letter": m.group(1).upper(), "text": m.group(2).strip()})
    return opts


def stem_of(block):
    lines = block.strip().split("\n")
    # drop option lines and answer lines and separators
    keep = []
    for ln in lines:
        s = ln.strip()
        if OPT_RE.match(ln) or s.startswith("**Answer:**") or re.match(r"^---+$", s):
            break
        keep.append(ln)
    return "\n".join(keep).strip()


def parse_key_table(body):
    """Return {qnum: {key, key_raw, tag, diff}} from the | **QN** | **X** | table."""
    keys = {}
    for m in KEYROW_RE.finditer(body):
        qn = int(m.group(1))
        raw = m.group(2).strip().strip("*").strip()
        rest = [c.strip().strip("*").strip() for c in m.group(3).strip().strip("|").split("|")]
        letter = re.match(r"^([A-E])\b", raw)
        if letter:
            keys[qn] = {"key": letter.group(1), "kind": "mc", "tag": rest[0] if len(rest) > 0 else "",
                        "diff": rest[1] if len(rest) > 1 else ""}
        else:
            keys[qn] = {"key": re.sub(r"\s+", " ", raw.strip("$ ")), "kind": "spr",
                        "tag": rest[0] if len(rest) > 0 else "", "diff": rest[1] if len(rest) > 1 else ""}
    return keys


def parse_rationales(body):
    """Map qnum -> markdown rationale chunk (sections after the key table)."""
    # rationale sections repeat ###/#### Question N headers AFTER the key table
    key_pos = body.find("Answer Key")
    tail = body[key_pos:] if key_pos != -1 else body
    chunks = {}
    pat = re.compile(r"^#{3,4}\s+Question\s+(\d+)\b[^\n]*$", re.M)
    matches = list(pat.finditer(tail))
    # only trust these if they carry solution markers
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(tail)
        chunk = tail[m.end():end].strip()
        if re.search(r"Correct Answer|Textual Proof|Method|Distractor|Solution|Rationale", chunk):
            chunks[int(m.group(1))] = chunk
    return chunks


def clean_flow_text(t):
    t = t.replace("SAT/", "").replace("index.html", "Portal").strip(" :")
    return t or "Open"


def parse_flow_links(body):
    """Teach -> Show -> Test footer links from the alignment section."""
    m = re.search(r"New System Alignment(.*?)(?:^---|\Z)", body, re.S | re.M)
    if not m:
        # fallback: any relative doc links (study-note footers)
        seen, out = set(), []
        for t, u in re.findall(r"\[([^\]]+?)\]\((\.\./[^)]+?)\)", body):
            if u not in seen:
                seen.add(u)
                out.append({"text": clean_flow_text(t), "url": u.strip()})
        return out[:6]
    return [{"text": clean_flow_text(t), "url": u.strip()}
            for t, u in re.findall(r"\[([^\]]+?)\]\(([^)]+?)\)", m.group(1))]


def parse_overview(body):
    m = re.search(r"^##\s+[^\n]*Overview[^\n]*\n(.*?)(?=^---+\s*$|^##\s+|\Z)", body, re.S | re.M)
    return m.group(1).strip() if m else ""


def parse_timer_seconds(body, n_items):
    m = re.search(r"(\d+)\s*Minutes?", body)
    if m:
        return int(m.group(1)) * 60
    m = re.search(r"~\s*(\d+)\s*seconds?\s+per\s+item", body, re.I)
    if m:
        return int(m.group(1)) * n_items
    return n_items * 95


def parse_md(md_path):
    text = md_path.read_text(encoding="utf-8")
    meta, body = frontmatter(text)
    title_m = re.search(r"^#\s+(.+)$", body, re.M)
    title = clean_title(title_m.group(1)) if title_m else md_path.stem.replace("_", " ").title()
    keys = parse_key_table(body)
    rats = parse_rationales(body)
    questions = []
    for num, head, block in split_questions(body):
        # skip rationale-section repeats (they carry solution markers, no options)
        opts = parse_options(block)
        is_spr_head = bool(re.search(r"produced.response|SPR", head, re.I))
        inline = INLINE_ANS_RE.search(block)
        k = keys.get(num, {})
        if inline and not opts:
            continue  # stray
        if not opts and not is_spr_head:
            # rationale repeat of a question header -> skip
            if re.search(r"Correct Answer|Textual Proof|Method|Distractor", block):
                continue
            if not inline:
                continue
        if opts:
            key = k.get("key", "") if k.get("kind", "mc") == "mc" else ""
            if inline and not key:
                key = inline.group(1)
            rat_md = rats.get(num, "")
            if not rat_md and inline:
                rat_md = "**Correct Answer: " + inline.group(1) + ".** " + inline.group(2).strip()
            questions.append({
                "n": num, "tag": head, "kind": "mc",
                "stem": md_blocks(stem_of(block)),
                "options": [{"L": o["letter"], "t": md_inline(o["text"])} for o in opts],
                "key": key,
                "rat": md_blocks(rat_md) if rat_md else "<p>Review the stimulus and eliminate each distractor.</p>",
                "diff": k.get("diff", ""), "domain": k.get("tag", ""),
            })
        else:
            key = k.get("key", "")
            rat_md = rats.get(num, "")
            questions.append({
                "n": num, "tag": head, "kind": "spr",
                "stem": md_blocks(stem_of(block)),
                "options": [], "key": key,
                "rat": md_blocks(rat_md) if rat_md else "<p>Enter an equivalent value (fractions and decimals accepted).</p>",
                "diff": k.get("diff", ""), "domain": k.get("tag", ""),
            })
    # sequential sanity: renumber check
    return {
        "title": title, "meta": meta, "questions": questions,
        "overview": md_blocks(parse_overview(body)) if parse_overview(body) else "",
        "seconds": parse_timer_seconds(body, max(len(questions), 1)),
        "flow": parse_flow_links(body),
    }


def norm_spr_key(raw):
    """Normalize an SPR key cell to a plain comparable answer string."""
    s = raw.strip()
    s = re.sub(r"\$+", "", s)
    m = re.match(r"^\\d?frac\{([^{}]+)\}\{([^{}]+)\}$", s)
    if m:
        return f"({m.group(1)})/({m.group(2)})"
    s = re.sub(r"\\(frac|dfrac|tfrac|cfrac)", "", s)
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"\\([a-zA-Z]+)", r"\1", s)
    return re.sub(r"\s+", " ", s).strip()


PAGE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@ | SAT Interactive Drill</title>
<style>
:root{--bg:#f8fafc;--surface:#fff;--text:#0f172a;--muted:#64748b;--primary:#7c3aed;--primary-d:#6d28d9;--primary-l:#ede9fe;--ok:#16a34a;--ok-l:#dcfce7;--bad:#dc2626;--bad-l:#fee2e2;--warn:#d97706;--warn-l:#fef3c7;--border:#e2e8f0;--radius:12px;--font:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',Consolas,monospace}
[data-theme="dark"]{--bg:#0b0f19;--surface:#131b2e;--text:#f1f5f9;--muted:#94a3b8;--primary:#a78bfa;--primary-d:#8b5cf6;--primary-l:#2e1065;--ok-l:#052e16;--bad-l:#450a0a;--warn-l:#451a03;--border:#334155}
*{box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.65;margin:0;padding:0 1rem 5rem}
.wrap{max-width:880px;margin:0 auto}
.topbar{position:sticky;top:0;z-index:50;background:var(--surface);border-bottom:1px solid var(--border);margin:0 -1rem;padding:.6rem 1rem}
.topbar-in{max-width:880px;margin:0 auto;display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;justify-content:space-between}
.brand{font-weight:800;font-size:.95rem}.brand a{color:var(--primary);text-decoration:none}
.crumbs{font-size:.8rem;color:var(--muted);margin:.9rem 0 .4rem}.crumbs a{color:var(--primary);text-decoration:none}
h1{font-size:1.6rem;line-height:1.3;border-left:6px solid var(--primary);padding-left:.9rem;margin:.4rem 0 1rem}
.meta{display:flex;flex-wrap:wrap;gap:.4rem 1rem;font-size:.82rem;color:var(--muted);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:.6rem 1rem;margin-bottom:1rem}
.controls{display:flex;flex-wrap:wrap;gap:.5rem;align-items:center;background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:.7rem 1rem;margin-bottom:1rem}
.btn{border:1px solid var(--border);background:var(--surface);color:var(--text);border-radius:8px;padding:.5rem .9rem;font-weight:700;font-size:.85rem;cursor:pointer;font-family:inherit}
.btn:hover{border-color:var(--primary);background:var(--primary-l)}
.btn.pri{background:var(--primary);border-color:var(--primary);color:#fff}
.btn.pri:hover{background:var(--primary-d)}
.btn.on{background:var(--primary-l);border-color:var(--primary);color:var(--primary)}
.timer{font-family:var(--mono);font-weight:700;font-size:1.05rem}
.timer.low{color:var(--bad)}
.progress{height:10px;background:var(--border);border-radius:6px;overflow:hidden;margin:.4rem 0 1rem}
.progress>div{height:100%;width:0;background:var(--primary);transition:width .25s}
.pills{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:1rem}
.pill{min-width:34px;height:34px;padding:0 8px;display:inline-flex;align-items:center;justify-content:center;border-radius:8px;border:1px solid var(--border);background:var(--surface);font-family:var(--mono);font-size:.82rem;font-weight:700;cursor:pointer;color:var(--text)}
.pill.cur{border-color:var(--primary);box-shadow:0 0 0 2px var(--primary-l)}
.pill.ans{background:var(--primary-l);border-color:var(--primary);color:var(--primary)}
.pill.flagged::after{content:" ⚑";color:var(--warn)}
.pill.good{background:var(--ok-l);border-color:var(--ok);color:var(--ok)}
.pill.miss{background:var(--bad-l);border-color:var(--bad);color:var(--bad)}
.qcard{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.3rem;margin:0 0 1.1rem;box-shadow:0 4px 6px -1px rgb(0 0 0/.05)}
.qcard.cur{border-color:var(--primary)}
.qtop{display:flex;gap:.6rem;align-items:center;margin-bottom:.6rem;flex-wrap:wrap}
.qnum{font-weight:800;color:var(--primary)}
.qtag{font-size:.72rem;font-weight:700;padding:2px 9px;border-radius:20px;background:var(--primary-l);color:var(--primary)}
.qtag.diff{background:var(--warn-l);color:var(--warn)}
.qacts{margin-left:auto;display:flex;gap:6px}
.iconbtn{border:1px solid var(--border);background:var(--surface);border-radius:8px;padding:.25rem .6rem;cursor:pointer;color:var(--muted);font-size:.9rem}
.iconbtn.flagged{color:var(--warn);border-color:var(--warn)}
.qstem{font-size:1.02rem;margin-bottom:.9rem}
.qstem p{margin:.55rem 0}
.opts{display:flex;flex-direction:column;gap:8px}
.opt{display:flex;gap:.7rem;align-items:flex-start;text-align:left;width:100%;padding:.65rem .8rem;border:1px solid var(--border);border-radius:9px;background:var(--surface);color:var(--text);cursor:pointer;font:inherit;font-size:.95rem}
.opt:hover:not(:disabled){border-color:var(--primary);background:var(--primary-l)}
.opt .ol{font-family:var(--mono);font-weight:700;border:1px solid var(--border);border-radius:6px;padding:0 8px;background:var(--bg);flex:none}
.opt.sel{border-color:var(--primary);background:var(--primary-l)}
.opt.good{border-color:var(--ok);background:var(--ok-l)}
.opt.good .ol{background:var(--ok);border-color:var(--ok);color:#fff}
.opt.miss{border-color:var(--bad);background:var(--bad-l)}
.opt.miss .ol{background:var(--bad);border-color:var(--bad);color:#fff}
.opt:disabled{cursor:default}
.spr-row{display:flex;gap:8px;flex-wrap:wrap}
.spr{flex:1;min-width:180px;border:1px solid var(--border);border-radius:9px;padding:.6rem .8rem;font:inherit;font-size:1rem;background:var(--surface);color:var(--text)}
.spr.good{border-color:var(--ok);background:var(--ok-l)}
.spr.miss{border-color:var(--bad);background:var(--bad-l)}
.rat{margin-top:.9rem;padding:.8rem 1rem;border-radius:9px;background:var(--bg);border-left:4px solid var(--primary);font-size:.92rem}
.rat p{margin:.45rem 0}.rat ul,.rat ol{margin:.4rem 0 .6rem;padding-left:1.3rem}.rat li{margin:.2rem 0}
.rat table{border-collapse:collapse;width:100%;margin:.6rem 0;font-size:.85rem}
.rat th,.rat td{border:1px solid var(--border);padding:.35rem .6rem;text-align:left}
.score{background:var(--surface);border:2px solid var(--primary);border-radius:var(--radius);padding:1.2rem 1.4rem;margin:1.2rem 0;display:none}
.score.show{display:block}
.score h2{margin:0 0 .4rem;font-size:1.3rem}
.flow{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.4rem 0}
.flow a{flex:1;min-width:150px;text-align:center;text-decoration:none;font-weight:700;font-size:.88rem;border:1px solid var(--primary);color:var(--primary);border-radius:9px;padding:.6rem}
.flow a:hover{background:var(--primary-l)}
.mx{white-space:nowrap}.mx-disp{display:block;text-align:center;margin:.7rem 0;font-size:1.08em;overflow-x:auto}
.mx-frac{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;margin:0 .1em}
.mx-frac>span{padding:0 .35em}.mx-frac>span:first-child{border-bottom:1.5px solid currentColor}
.mx-root{border-top:1.5px solid currentColor;padding:0 .1em}
.mx-cases{display:inline-flex;align-items:stretch;gap:.3em;vertical-align:middle}
.mx-brace{font-size:1.6em;line-height:1}
.mx-rows{display:inline-flex;flex-direction:column;gap:.15em}
code{font-family:var(--mono);font-size:.85em;background:var(--primary-l);padding:.1rem .35rem;border-radius:6px}
pre{background:#0f172a;color:#e2e8f0;padding:1rem;border-radius:var(--radius);overflow:auto}
pre code{background:none;color:inherit;padding:0}
table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.9rem}
th,td{border:1px solid var(--border);padding:.45rem .65rem;text-align:left}
blockquote{border-left:4px solid var(--primary);margin:.8rem 0;padding:.3rem 1rem;background:var(--surface);border-radius:0 var(--radius) var(--radius) 0}
.overview{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1rem 1.2rem;margin-bottom:1.1rem;font-size:.92rem}
.overview ul{margin:.4rem 0 .6rem;padding-left:1.3rem}
@media print{.topbar,.controls,.pills,.qacts,.flow,#st-bar,#st-show,#st-canvas,.st-p,#st-tip,#st-toast{display:none!important}.rat{display:block!important}.qcard{break-inside:avoid}}
</style>
</head>
<body>
<div class="topbar"><div class="topbar-in">
<div class="brand">@@BADGE@@ <a href="@@CRUMB_UP@@">SAT Portal</a> &rsaquo; @@CRUMB_CAT@@</div>
<div style="display:flex;gap:.5rem;align-items:center;flex-wrap:wrap">
<span class="timer" id="mx-timer">--:--</span>
<button class="btn on" id="mx-mode" title="Practice: instant feedback. Exam: feedback on submit.">Practice mode</button>
<button class="btn" id="mx-theme" title="Dark / light">🌓</button>
<button class="btn pri" id="mx-submit">Submit</button>
</div></div></div>
<div class="wrap">
<div class="crumbs"><a href="@@CRUMB_UP@@">&larr; SAT Portal</a> &rsaquo; @@CRUMB_CAT@@</div>
<h1>@@TITLE@@</h1>
<div class="meta">@@META@@</div>
<div class="overview">@@OVERVIEW@@</div>
<div class="controls">
<button class="btn" id="mx-prev">← Prev</button>
<button class="btn" id="mx-next">Next →</button>
<button class="btn" id="mx-unflag" title="Jump to first unanswered">Unanswered ↓</button>
<button class="btn" id="mx-reset" title="Clear answers on this device">Reset</button>
<span style="font-size:.82rem;color:var(--muted)">Keys: A–D / 1–4 answer • F flag • ←/→ move</span>
</div>
<div class="progress"><div id="mx-bar"></div></div>
<div class="pills" id="mx-pills"></div>
<div id="mx-cards"></div>
<div class="score" id="mx-score"></div>
<div class="flow">@@FLOW@@</div>
</div>
<script>
(function(){
"use strict";
var Q=@@DATA@@;
var PAGE=(function(){try{var p=location.pathname.split('/').filter(Boolean);return 'sat:'+p.slice(-2).join('/');}catch(e){return 'sat:page';}})();
var S={mode:'practice',submitted:false,current:0,ans:{},flag:{},left:@@SECONDS@@,timerOn:true};
try{var sv=JSON.parse(localStorage.getItem(PAGE)||'null');if(sv&&sv.ans){S.ans=sv.ans;S.flag=sv.flag||{};}}catch(e){}
function save(){try{localStorage.setItem(PAGE,JSON.stringify({ans:S.ans,flag:S.flag}));}catch(e){}}
function $(id){return document.getElementById(id);}
function esc(s){return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;');}
function answeredCount(){var c=0;Q.forEach(function(q,i){if(S.ans[i]!==undefined&&S.ans[i]!==''&&S.ans[i]!==null)c++;});return c;}
function sprNorm(s){return String(s).replace(/\s+/g,'').replace(/,/g,'');}
function sprNum(s){var m=sprNorm(s).match(/^(-?\d+(?:\.\d+)?)\/(-?\d+(?:\.\d+)?)$/);if(m&&+m[2]!==0)return +m[1]/+m[2];var v=parseFloat(sprNorm(s));return isNaN(v)?null:v;}
function sprEqual(a,b){var x=sprNorm(a),y=sprNorm(b);if(!x||!y)return false;if(x===y)return true;var p1=x.match(/^\(?(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\)?$/),p2=y.match(/^\(?(-?\d+(?:\.\d+)?),(-?\d+(?:\.\d+)?)\)?$/);if(p1&&p2)return Math.abs(+p1[1]-+p2[1])<1e-9&&Math.abs(+p1[2]-+p2[2])<1e-9;var v1=sprNum(x),v2=sprNum(y);return v1!==null&&v2!==null&&Math.abs(v1-v2)<1e-9;}
function isCorrect(i){var q=Q[i],a=S.ans[i];if(a===undefined||a===''||a===null)return null;if(q.kind==='spr')return sprEqual(a,q.key);return a===q.key;}
function render(){
  var host=$('mx-cards');host.innerHTML='';
  Q.forEach(function(q,i){
    var card=document.createElement('article');card.className='qcard'+(i===S.current?' cur':'');card.id='card-'+i;
    var tags=(q.diff?'<span class="qtag diff">'+esc(q.diff)+'</span>':'')+(q.domain?'<span class="qtag">'+esc(q.domain)+'</span>':'');
    var h='<div class="qtop"><span class="qnum">Q'+q.n+'</span>'+tags+'<span class="qacts"><button class="iconbtn'+(S.flag[i]?' flagged':'')+'" data-flag="'+i+'" title="Flag (F)">⚑</button></span></div>';
    h+='<div class="qstem">'+q.stem+'</div>';
    if(q.kind==='spr'){
      var v=S.ans[i]===undefined?'':esc(S.ans[i]);
      h+='<div class="spr-row"><input class="spr" id="spr-'+i+'" value="'+v+'" placeholder="Your answer" inputmode="decimal" autocomplete="off"><button class="btn pri" data-check="'+i+'">Check</button></div><div class="rat" id="rat-'+i+'" hidden></div>';
    }else{
      h+='<div class="opts">'+q.options.map(function(o){
        var cls='opt'+(S.ans[i]===o.L?' sel':'');
        return '<button class="'+cls+'" data-q="'+i+'" data-l="'+o.L+'"><span class="ol">'+o.L+'</span><span>'+o.t+'</span></button>';
      }).join('')+'</div><div class="rat" id="rat-'+i+'" hidden></div>';
    }
    card.innerHTML=h;host.appendChild(card);
  });
  renderPills();updateBar();refresh(true);
}
function renderPills(){
  $('mx-pills').innerHTML=Q.map(function(q,i){
    var c='pill'+(i===S.current?' cur':'')+((S.ans[i]!==undefined&&S.ans[i]!==''&&S.ans[i]!==null)?' ans':'')+(S.flag[i]?' flagged':'');
    return '<button class="'+c+'" data-goto="'+i+'">'+q.n+'</button>';
  }).join('');
}
function updateBar(){$('mx-bar').style.width=Math.round(answeredCount()/Q.length*100)+'%';}
function setCurrent(i){S.current=Math.max(0,Math.min(Q.length-1,i));Array.prototype.forEach.call(document.querySelectorAll('.qcard.cur'),function(e){e.classList.remove('cur');});var c=$('card-'+S.current);if(c)c.classList.add('cur');renderPills();}
function reveal(i){
  var q=Q[i],rat=$('rat-'+i);if(!rat)return;
  var ok=isCorrect(i);
  if(q.kind==='spr'){
    var inp=$('spr-'+i);if(inp){inp.classList.remove('good','miss');if(ok!==null)inp.classList.add(ok?'good':'miss');}
  }else{
    Array.prototype.forEach.call(document.querySelectorAll('#card-'+i+' .opt'),function(b){
      b.classList.remove('good','miss');
      if(b.getAttribute('data-l')===q.key)b.classList.add('good');
      else if(b.getAttribute('data-l')===S.ans[i]&&ok===false)b.classList.add('miss');
    });
  }
  rat.innerHTML=(ok===true?'<strong style="color:var(--ok)">✓ Correct.</strong> ':(ok===false?'<strong style="color:var(--bad)">✗ Not quite.</strong> Correct answer: <strong>'+esc(q.key)+'</strong>. ':''))+q.rat;
  rat.hidden=false;
}
function refresh(revealAnswered){
  Q.forEach(function(q,i){
    var rat=$('rat-'+i);if(!rat)return;
    var show=S.submitted||(S.mode==='practice'&&S.ans[i]!==undefined&&S.ans[i]!==''&&S.ans[i]!==null);
    if(show&&revealAnswered!==false)reveal(i);else if(!show){rat.hidden=true;
      if(q.kind==='spr'){var inp=$('spr-'+i);if(inp)inp.classList.remove('good','miss');}
      else Array.prototype.forEach.call(document.querySelectorAll('#card-'+i+' .opt'),function(b){b.classList.remove('good','miss');});}
  });
  updateBar();renderScore();
}
function selectMC(i,L){
  if(S.submitted)return;
  S.ans[i]=L;save();setCurrent(i);
  Array.prototype.forEach.call(document.querySelectorAll('#card-'+i+' .opt'),function(b){b.classList.toggle('sel',b.getAttribute('data-l')===L);});
  if(S.mode==='practice')reveal(i);else{updateBar();renderPills();}
}
function submitAll(){
  S.submitted=true;save();
  var right=0;Q.forEach(function(q,i){if(isCorrect(i)===true)right++;reveal(i);});
  var pct=Math.round(right/Q.length*100);
  var sc=$('mx-score');
  var miss=Q.map(function(q,i){return i;}).filter(function(i){return isCorrect(i)!==true;});
  sc.innerHTML='<h2>Score: '+right+' / '+Q.length+' ('+pct+'%)</h2><p>'+(miss.length?'Review: '+miss.map(function(i){return '<a href="#card-'+i+'" style="color:var(--primary)">Q'+Q[i].n+'</a>';}).join(' · '):'Perfect — nothing to review.')+'</p><p><button class="btn" id="mx-retry">Retry missed ('+miss.length+')</button> <button class="btn" id="mx-again">Restart all</button></p>';
  sc.classList.add('show');renderPills();
  var rt=$('mx-retry');if(rt)rt.onclick=function(){miss.forEach(function(i){delete S.ans[i];});S.submitted=false;save();sc.classList.remove('show');refresh(false);render();if(miss.length)setCurrent(miss[0]);};
  var ag=$('mx-again');if(ag)ag.onclick=function(){S.ans={};S.submitted=false;save();sc.classList.remove('show');refresh(false);render();setCurrent(0);};
  sc.scrollIntoView({behavior:'smooth'});
}
function renderScore(){}
document.addEventListener('click',function(e){
  var o=e.target.closest&&e.target.closest('.opt');if(o){selectMC(+o.getAttribute('data-q'),o.getAttribute('data-l'));return;}
  var c=e.target.closest&&e.target.closest('[data-check]');if(c){var i=+c.getAttribute('data-check');var inp=$('spr-'+i);S.ans[i]=inp.value;save();setCurrent(i);if(S.mode==='practice'||S.submitted)reveal(i);else{updateBar();renderPills();}return;}
  var f=e.target.closest&&e.target.closest('[data-flag]');if(f){var j=+f.getAttribute('data-flag');S.flag[j]=!S.flag[j];save();f.classList.toggle('flagged',!!S.flag[j]);renderPills();return;}
  var g=e.target.closest&&e.target.closest('[data-goto]');if(g){setCurrent(+g.getAttribute('data-goto'));var cd=$('card-'+S.current);if(cd)cd.scrollIntoView({behavior:'smooth',block:'start'});return;}
});
$('mx-submit').onclick=submitAll;
$('mx-prev').onclick=function(){setCurrent(S.current-1);var c=$('card-'+S.current);if(c)c.scrollIntoView({behavior:'smooth'});};
$('mx-next').onclick=function(){setCurrent(S.current+1);var c=$('card-'+S.current);if(c)c.scrollIntoView({behavior:'smooth'});};
$('mx-unflag').onclick=function(){for(var i=0;i<Q.length;i++){if(S.ans[i]===undefined||S.ans[i]===''||S.ans[i]===null){setCurrent(i);var c=$('card-'+i);if(c)c.scrollIntoView({behavior:'smooth'});return;}}};
$('mx-reset').onclick=function(){if(confirm('Clear all answers on this page?')){S.ans={};S.flag={};S.submitted=false;save();$('mx-score').classList.remove('show');render();}};
$('mx-mode').onclick=function(){S.mode=(S.mode==='practice')?'exam':'practice';var b=$('mx-mode');b.textContent=(S.mode==='practice'?'Practice mode':'Exam mode');b.classList.toggle('on',S.mode==='practice');refresh(false);};
$('mx-theme').onclick=function(){var h=document.documentElement;h.setAttribute('data-theme',h.getAttribute('data-theme')==='dark'?'light':'dark');};
document.addEventListener('keydown',function(e){
  var t=e.target;if(t&&(t.tagName==='TEXTAREA'||t.tagName==='INPUT'))return;
  var k=e.key.toLowerCase();
  if(['a','b','c','d'].indexOf(k)>-1&&Q[S.current]&&Q[S.current].kind==='mc'){selectMC(S.current,k.toUpperCase());}
  else if(['1','2','3','4'].indexOf(k)>-1&&Q[S.current]&&Q[S.current].kind==='mc'){selectMC(S.current,'ABCD'[+k-1]);}
  else if(k==='f'){S.flag[S.current]=!S.flag[S.current];save();render();}
  else if(k==='arrowdown'){e.preventDefault();setCurrent(S.current+1);}
  else if(k==='arrowup'){e.preventDefault();setCurrent(S.current-1);}
});
var totalSec=@@SECONDS@@,left=totalSec,timerEl=$('mx-timer');
function tick(){var m=Math.floor(left/60),s=left%60;timerEl.textContent=(m<10?'0':'')+m+':'+(s<10?'0':'')+s;timerEl.classList.toggle('low',left<300);if(left>0)left--;}
tick();setInterval(tick,1000);
window.addEventListener('beforeprint',function(){Q.forEach(function(q,i){var r=$('rat-'+i);if(r){r.hidden=false;}});});
render();
})();
</script>
@@ST@@
</body>
</html>
"""


def build_page(parsed, crumb_up, crumb_cat, meta_html):
    data = []
    for q in parsed["questions"]:
        key = q["key"]
        if q["kind"] == "spr":
            key = norm_spr_key(key)
        data.append({"n": q["n"], "kind": q["kind"], "stem": q["stem"],
                     "options": q["options"], "key": key, "rat": q["rat"],
                     "diff": q.get("diff", ""), "domain": q.get("domain", "")})
    flow = "".join(f'<a href="{f["url"]}">{f["text"]}</a>' for f in parsed["flow"])
    st = ""
    if _st_snippet:
        try:
            st = _st_snippet()
        except Exception as e:
            print(f"  (toolbar unavailable: {e})")
    page = PAGE_TEMPLATE
    page = page.replace("@@TITLE@@", parsed["title"].replace("&", "&amp;").replace("<", "&lt;"))
    page = page.replace("@@BADGE@@", "SAT")
    page = page.replace("@@CRUMB_UP@@", crumb_up)
    page = page.replace("@@CRUMB_CAT@@", crumb_cat)
    page = page.replace("@@META@@", meta_html)
    page = page.replace("@@OVERVIEW@@", parsed["overview"])
    page = page.replace("@@DATA@@", json.dumps(data, ensure_ascii=False))
    page = page.replace("@@SECONDS@@", str(parsed["seconds"]))
    page = page.replace("@@FLOW@@", flow)
    page = page.replace("@@ST@@", "<!-- student-tools v1 -->\n" + st if st else "")
    return page


PROSE_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>@@TITLE@@ | SAT Study Guide</title>
<style>
:root{--bg:#f8fafc;--surface:#fff;--text:#0f172a;--muted:#64748b;--primary:#7c3aed;--primary-d:#6d28d9;--primary-l:#ede9fe;--border:#e2e8f0;--radius:12px;--font:'Plus Jakarta Sans',system-ui,-apple-system,'Segoe UI',sans-serif;--mono:'JetBrains Mono',Consolas,monospace}
[data-theme="dark"]{--bg:#0b0f19;--surface:#131b2e;--text:#f1f5f9;--muted:#94a3b8;--primary:#a78bfa;--primary-d:#8b5cf6;--primary-l:#2e1065;--border:#334155}
*{box-sizing:border-box}body{font-family:var(--font);background:var(--bg);color:var(--text);line-height:1.7;margin:0;padding:0 1rem 5rem}
.wrap{max-width:880px;margin:0 auto}
.topbar{position:sticky;top:0;z-index:50;background:var(--surface);border-bottom:1px solid var(--border);margin:0 -1rem;padding:.6rem 1rem}
.topbar-in{max-width:880px;margin:0 auto;display:flex;flex-wrap:wrap;gap:.5rem 1rem;align-items:center;justify-content:space-between}
.brand{font-weight:800;font-size:.95rem}.brand a{color:var(--primary);text-decoration:none}
.crumbs{font-size:.8rem;color:var(--muted);margin:.9rem 0 .4rem}.crumbs a{color:var(--primary);text-decoration:none}
h1{font-size:1.6rem;line-height:1.3;border-left:6px solid var(--primary);padding-left:.9rem;margin:.4rem 0 1rem}
h2{font-size:1.3rem;margin-top:2rem;border-bottom:2px solid var(--border);padding-bottom:.3rem}
h3{font-size:1.08rem;margin-top:1.5rem}
.meta{display:flex;flex-wrap:wrap;gap:.4rem 1rem;font-size:.82rem;color:var(--muted);background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:.6rem 1rem;margin-bottom:1rem}
.guide{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.2rem 1.4rem;box-shadow:0 4px 6px -1px rgb(0 0 0/.05)}
.guide p{margin:.65rem 0}.guide ul,.guide ol{margin:.5rem 0 .9rem;padding-left:1.4rem}.guide li{margin:.28rem 0}
.flow{display:flex;flex-wrap:wrap;gap:.6rem;margin:1.4rem 0}
.flow a{flex:1;min-width:150px;text-align:center;text-decoration:none;font-weight:700;font-size:.88rem;border:1px solid var(--primary);color:var(--primary);border-radius:9px;padding:.6rem}
.flow a:hover{background:var(--primary-l)}
.mx{white-space:nowrap}.mx-disp{display:block;text-align:center;margin:.7rem 0;font-size:1.08em;overflow-x:auto}
.mx-frac{display:inline-flex;flex-direction:column;vertical-align:middle;text-align:center;margin:0 .1em}
.mx-frac>span{padding:0 .35em}.mx-frac>span:first-child{border-bottom:1.5px solid currentColor}
.mx-root{border-top:1.5px solid currentColor;padding:0 .1em}
.mx-cases{display:inline-flex;align-items:stretch;gap:.3em;vertical-align:middle}
.mx-brace{font-size:1.6em;line-height:1}
.mx-rows{display:inline-flex;flex-direction:column;gap:.15em}
code{font-family:var(--mono);font-size:.85em;background:var(--primary-l);padding:.1rem .35rem;border-radius:6px}
pre{background:#0f172a;color:#e2e8f0;padding:1rem;border-radius:var(--radius);overflow:auto}
pre code{background:none;color:inherit;padding:0}
table{border-collapse:collapse;width:100%;margin:.8rem 0;font-size:.9rem}
th,td{border:1px solid var(--border);padding:.45rem .65rem;text-align:left}
blockquote{border-left:4px solid var(--primary);margin:.8rem 0;padding:.3rem 1rem;background:var(--surface);border-radius:0 var(--radius) var(--radius) 0}
@media print{.topbar,.flow,#st-bar,#st-show,#st-canvas,.st-p,#st-tip,#st-toast{display:none!important}}
</style>
</head>
<body>
<div class="topbar"><div class="topbar-in">
<div class="brand">SAT <a href="@@CRUMB_UP@@">SAT Portal</a> &rsaquo; @@CRUMB_CAT@@</div>
<div><button class="btn" id="mx-theme" title="Dark / light" style="border:1px solid var(--border);background:var(--surface);color:var(--text);border-radius:8px;padding:.5rem .9rem;font-weight:700;cursor:pointer">🌓 Theme</button></div>
</div></div>
<div class="wrap">
<div class="crumbs"><a href="@@CRUMB_UP@@">&larr; SAT Portal</a> &rsaquo; @@CRUMB_CAT@@</div>
<h1>@@TITLE@@</h1>
<div class="meta">@@META@@</div>
<div class="guide">@@BODY@@</div>
<div class="flow">@@FLOW@@</div>
</div>
<script>
document.getElementById('mx-theme').onclick=function(){var h=document.documentElement;h.setAttribute('data-theme',h.getAttribute('data-theme')==='dark'?'light':'dark');};
</script>
@@ST@@
</body>
</html>
"""


def build_prose_page(md_path, parsed):
    from sat_tex import md_blocks as _blocks
    text = md_path.read_text(encoding="utf-8")
    _, body = frontmatter(text)
    body = re.split(r"^##\s+New System Alignment", body, maxsplit=1, flags=re.M)[0]
    body_html = _blocks(body)
    m = parsed["meta"]
    bits = []
    if m.get("target_level"):
        bits.append(f"<span><b>Level:</b> {m['target_level']}</span>")
    if m.get("topic"):
        bits.append(f"<span><b>Topic:</b> {m['topic']}</span>")
    bits.append(f"<span><b>Type:</b> {m.get('content_type', 'Study Guide')}</span>")
    flow = "".join(f'<a href="{f["url"]}">{f["text"]}</a>' for f in parsed["flow"])
    depth = len(md_path.parent.relative_to(WORKSPACE_ROOT).parts)
    crumb_up = "../" * (depth - 1) + "index.html"
    st = ""
    if _st_snippet:
        try:
            st = _st_snippet()
        except Exception as e:
            print(f"  (toolbar unavailable: {e})")
    page = PROSE_TEMPLATE
    page = page.replace("@@TITLE@@", parsed["title"].replace("&", "&amp;").replace("<", "&lt;"))
    page = page.replace("@@CRUMB_UP@@", crumb_up)
    page = page.replace("@@CRUMB_CAT@@", md_path.parent.name)
    page = page.replace("@@META@@", "".join(bits))
    page = page.replace("@@BODY@@", body_html)
    page = page.replace("@@FLOW@@", flow)
    page = page.replace("@@ST@@", "<!-- student-tools v1 -->\n" + st if st else "")
    return page


def meta_html_for(parsed, rel):
    m = parsed["meta"]
    bits = [f"<span><b>Questions:</b> {len(parsed['questions'])}</span>"]
    if m.get("target_level"):
        bits.append(f"<span><b>Level:</b> {m['target_level']}</span>")
    if m.get("topic"):
        bits.append(f"<span><b>Topic:</b> {m['topic']}</span>")
    secs = parsed["seconds"]
    bits.append(f"<span><b>Suggested time:</b> {secs // 60} min</span>")
    return "".join(bits)


def drill_sources():
    out = []
    for md in sorted((WORKSPACE_ROOT / "SAT").rglob("*.md")):
        if md.name == "README.md":
            continue
        out.append(md)
    return out


def main():
    args = sys.argv[1:]
    check_only = "--check" in args
    if "--all" in args or check_only:
        sources = drill_sources()
    else:
        sources = [Path(a).resolve() if not Path(a).is_absolute() else Path(a)
                   for a in args if not a.startswith("--")]
    total_q, built, skipped = 0, 0, []
    for md in sources:
        try:
            parsed = parse_md(md)
        except Exception as e:
            print(f"[ERROR] {md}: {e}")
            continue
        nq = len(parsed["questions"])
        missing = sum(1 for q in parsed["questions"] if not q["key"])
        total_q += nq
        rel = md.relative_to(WORKSPACE_ROOT).as_posix()
        print(f"{rel}: {nq} Qs, {missing} missing keys, {parsed['seconds'] // 60} min")
        if check_only:
            if nq == 0:
                skipped.append(rel)
            continue
        if nq == 0:
            if md.name == "README.md":
                skipped.append(rel)
                continue
            md.with_suffix(".html").write_text(build_prose_page(md, parsed), encoding="utf-8")
            built += 1
            continue
        depth = len(md.parent.relative_to(WORKSPACE_ROOT).parts)
        crumb_up = "../" * (depth - 1) + "index.html"  # twin sits next to its .md
        cat = md.parent.name
        page = build_page(parsed, crumb_up, cat, meta_html_for(parsed, rel))
        md.with_suffix(".html").write_text(page, encoding="utf-8")
        built += 1
    print(f"\nTotal questions parsed: {total_q} | pages built: {built} | prose-only skipped: {len(skipped)}")
    for s in skipped:
        print(f"  (prose) {s}")


if __name__ == "__main__":
    main()

