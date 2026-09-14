#!/usr/bin/env python3
"""Regenerate navigation index.html files for SAT content folders.

Lists subdirectories + .html pages (never .md), with titles scraped from
each page's <title>. Skips: SAT/index.html (master portal), SAT/webapp/**.
Safe to re-run.
"""
import os
import re

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SAT = os.path.join(BASE, 'SAT')
SKIP_DIRS = {'webapp', '.git'}

CSS = ("body{font-family:'Plus Jakarta Sans',system-ui,sans-serif;background:#f8fafc;"
       "color:#0f172a;padding:2rem;line-height:1.6}.wrap{max-width:900px;margin:0 auto}"
       "h1{font-size:1.8rem;border-left:6px solid #2b7fff;padding-left:1rem}"
       "ul{line-height:2.1;list-style:none;padding:0}.dir::before{content:'\\1F4C1  '}"
       ".page::before{content:'\\1F4C4  '}a{color:#2b7fff;text-decoration:none}"
       "a:hover{text-decoration:underline}.crumbs{font-size:.82rem;color:#64748b}"
       ".meta{font-size:.8rem;color:#64748b}")

def page_title(path):
    try:
        c = open(path, encoding='utf-8').read(4000)
    except OSError:
        return os.path.basename(path)
    m = re.search(r'<title>(.*?)</title>', c, re.S)
    if not m:
        return os.path.basename(path)
    t = m.group(1).strip().split('|')[0].strip()
    return t or os.path.basename(path)

def pretty(name):
    return name.replace('_', ' ').title()

def build_index(d):
    rel = os.path.relpath(d, SAT).replace(os.sep, '/')
    depth = 0 if rel == '.' else rel.count('/') + 1
    up = '../' * depth
    entries = sorted(os.listdir(d))
    subdirs = [e for e in entries
               if os.path.isdir(os.path.join(d, e)) and e not in SKIP_DIRS and not e.startswith('.')]
    pages = [e for e in entries
             if e.lower().endswith('.html') and e != 'index.html']
    lis = []
    for s in subdirs:
        lis.append('<li class="dir"><a href="%s/index.html">%s</a> <span class="meta">section</span></li>'
                   % (s, pretty(s)))
    for p in pages:
        lis.append('<li class="page"><a href="%s">%s</a></li>' % (p, page_title(os.path.join(d, p))))
    if not lis:
        return False
    label = 'SAT' if rel == '.' else pretty(os.path.basename(d))
    html = ('<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1.0">'
            '<title>SAT \u2014 %s</title><style>%s</style></head><body><div class="wrap">'
            '<div class="crumbs"><a href="%sindex.html">SAT Portal</a> &rsaquo; %s</div>'
            '<h1>SAT \u2014 %s</h1><ul>%s</ul>'
            '<p class="crumbs"><a href="%sindex.html">&larr; SAT Portal</a></p>'
            '</div></body></html>' % (label, CSS, up, rel, label, ''.join(lis), up))
    with open(os.path.join(d, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    return True

TARGETS = ['Practice_Modules', 'Question_Banks', 'Reading_Writing', 'Math',
           'Study_Notes', 'Vocabulary', 'Show', 'Test',
           'Reading_Writing/Craft_and_Structure',
           'Reading_Writing/Expression_of_Ideas',
           'Reading_Writing/Information_and_Ideas',
           'Reading_Writing/Standard_English_Conventions',
           'Math/Algebra', 'Math/Advanced_Math',
           'Math/Problem_Solving_and_Data_Analysis',
           'Math/Geometry_and_Trigonometry']

if __name__ == '__main__':
    for t in TARGETS:
        d = os.path.join(SAT, *t.split('/'))
        if os.path.isdir(d):
            print(('built ' if build_index(d) else 'empty ') + t)
