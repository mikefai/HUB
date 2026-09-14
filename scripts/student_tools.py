#!/usr/bin/env python3
"""Student-tools toolbar snippet for SAT study pages.

Injects a self-contained, zero-dependency toolbar before </body>:
pen (draw on page), highlighter, notes panel, calculator and B1 vocabulary
glosses. All state persists per page in localStorage. Idempotent.
"""

import json
import re
from pathlib import Path

try:
    from student_tools_vocab import VOCAB
except ImportError:  # allow `python scripts/add_student_tools.py` style runs
    import sys as _sys
    _sys.path.insert(0, str(Path(__file__).parent))
    from student_tools_vocab import VOCAB

VERSION = "v1"
MARKER = "<!-- student-tools v1 -->"

CSS = r"""
#st-bar{position:fixed;left:50%;transform:translateX(-50%);bottom:12px;z-index:9999;display:flex;gap:6px;align-items:center;background:#0f172a;color:#fff;padding:8px 10px;border-radius:14px;box-shadow:0 10px 25px rgb(0 0 0/.35);max-width:96vw;overflow-x:auto;font-family:system-ui,sans-serif}
#st-bar button{border:1px solid #334155;background:#1e293b;color:#fff;border-radius:9px;padding:7px 10px;font-size:.82rem;font-weight:700;cursor:pointer;white-space:nowrap}
#st-bar button:hover{background:#334155}
#st-bar button.st-on{background:#2b7fff;border-color:#2b7fff}
#st-show{position:fixed;right:12px;bottom:12px;z-index:9999;display:none;background:#0f172a;color:#fff;border:none;border-radius:12px;padding:10px 14px;font-weight:800;cursor:pointer;box-shadow:0 10px 25px rgb(0 0 0/.35)}
#st-canvas{position:absolute;top:0;left:0;z-index:9998;touch-action:none;pointer-events:none}
.st-p{position:fixed;top:64px;right:12px;width:min(340px,92vw);max-height:80vh;overflow:auto;background:#fff;border:1px solid #e2e8f0;border-radius:12px;box-shadow:0 14px 34px rgb(0 0 0/.25);z-index:10000;display:none;font-family:system-ui,sans-serif;color:#0f172a}
.st-p.open{display:block}
.st-p header{display:flex;justify-content:space-between;align-items:center;padding:.6rem .9rem;border-bottom:1px solid #e2e8f0;font-weight:800;cursor:default}
.st-p .body{padding:.8rem .9rem}
.st-p textarea{width:100%;min-height:180px;border:1px solid #cbd5e1;border-radius:8px;padding:.6rem;font:inherit;font-size:.9rem;resize:vertical}
.st-row{display:flex;gap:6px;flex-wrap:wrap;margin-top:.6rem;align-items:center}
.st-btn{border:1px solid #cbd5e1;background:#f1f5f9;border-radius:8px;padding:6px 10px;font-weight:700;font-size:.8rem;cursor:pointer;color:#0f172a}
.st-btn:hover{background:#e2e8f0}
.st-sw{width:26px;height:26px;border-radius:50%;border:2px solid #cbd5e1;cursor:pointer}
.st-sw.sel{border-color:#0f172a}
#st-calc-p{width:min(300px,92vw)}
#st-calc-head{cursor:grab}
#st-calc-disp{background:#0f172a;color:#fff;border-radius:8px;padding:.6rem .7rem;text-align:right;font-size:1.25rem;font-weight:800;min-height:2.2em;overflow-x:auto;white-space:nowrap}
#st-calc-hist{text-align:right;color:#64748b;font-size:.75rem;min-height:1.2em;margin-top:2px}
#st-calc-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:6px;margin-top:.6rem}
#st-calc-grid button{border:1px solid #cbd5e1;background:#f8fafc;border-radius:8px;padding:.55rem 0;font-size:.95rem;font-weight:800;cursor:pointer;color:#0f172a}
#st-calc-grid button:hover{background:#e2e8f0}
#st-calc-grid button.op{background:#dbeafe;border-color:#93c5fd}
#st-calc-grid button.eq{background:#2b7fff;color:#fff;border-color:#2b7fff}
.st-hl{background:#fef08a;border-radius:2px}
button.st-vocab{background:none;border:none;border-bottom:2px dotted #2b7fff;color:inherit;font:inherit;padding:0;cursor:pointer}
#st-tip{position:fixed;z-index:10001;display:none;max-width:min(300px,86vw);background:#0f172a;color:#fff;border-radius:10px;padding:.6rem .8rem;font-size:.85rem;box-shadow:0 10px 25px rgb(0 0 0/.4);font-family:system-ui,sans-serif}
#st-tip b{color:#93c5fd}
#st-toast{position:fixed;bottom:70px;left:50%;transform:translateX(-50%);z-index:10002;display:none;background:#0f172a;color:#fff;border-radius:10px;padding:.55rem 1rem;font-size:.85rem;font-weight:700;font-family:system-ui,sans-serif;box-shadow:0 10px 25px rgb(0 0 0/.4)}
@media print{#st-bar,#st-show,#st-canvas,.st-p,#st-tip,#st-toast{display:none!important}}
"""

HTML = r"""
<canvas id="st-canvas"></canvas>
<div id="st-bar" role="toolbar" aria-label="Student tools">
<button type="button" data-act="pen" title="Draw on the page">🖊 Pen</button>
<button type="button" data-act="hl" title="Highlight the selected text">🖍 Highlight</button>
<button type="button" data-act="notes" title="Take notes (saved on this device)">📝 Notes</button>
<button type="button" data-act="calc" title="Calculator">🧮 Calc</button>
<button type="button" data-act="words" title="Show word meanings for hard words">📖 Words</button>
<button type="button" data-act="clear" title="Clear pen + highlights on this page">🗑 Clear</button>
<button type="button" data-act="hide" title="Hide toolbar">–</button>
</div>
<button type="button" id="st-show" title="Show student tools">🧰 Tools</button>
<div class="st-p" id="st-p-pen"><header><span>🖊 Pen</span><button type="button" class="st-btn" data-close="st-p-pen">✖</button></header><div class="body"><div class="st-row" id="st-swatches">
<button type="button" class="st-sw sel" data-c="#1d4ed8" style="background:#1d4ed8" title="Blue"></button>
<button type="button" class="st-sw" data-c="#111111" style="background:#111111" title="Black"></button>
<button type="button" class="st-sw" data-c="#dc2626" style="background:#dc2626" title="Red"></button>
<button type="button" class="st-sw" data-c="#059669" style="background:#059669" title="Green"></button>
<button type="button" class="st-btn" data-w="2">Thin</button>
<button type="button" class="st-btn" data-w="4">Med</button>
<button type="button" class="st-btn" data-w="7">Thick</button>
<button type="button" class="st-btn" data-er="1" title="Erase strokes">🧽 Eraser</button>
</div><div class="st-row"><button type="button" class="st-btn" data-act="pen-clear">Clear drawings</button></div></div></div>
<div class="st-p" id="st-p-notes"><header><span>📝 My notes</span><button type="button" class="st-btn" data-close="st-p-notes">✖</button></header><div class="body"><textarea id="st-notes-area" placeholder="Type your notes here…"></textarea><div class="st-row"><span id="st-notes-meta" style="font-size:.78rem;color:#64748b"></span></div><div class="st-row"><button type="button" class="st-btn" data-act="notes-copy">Copy</button><button type="button" class="st-btn" data-act="notes-clear">Clear</button></div></div></div>
<div class="st-p" id="st-calc-p"><header id="st-calc-head"><span>🧮 Calculator</span><button type="button" class="st-btn" data-close="st-calc-p">✖</button></header><div class="body"><div id="st-calc-disp">0</div><div id="st-calc-hist"></div><div id="st-calc-grid">
<button type="button" data-k="C" class="op">C</button><button type="button" data-k="bk" class="op">⌫</button><button type="button" data-k="%" class="op">%</button><button type="button" data-k="/" class="op">÷</button>
<button type="button" data-k="7">7</button><button type="button" data-k="8">8</button><button type="button" data-k="9">9</button><button type="button" data-k="*" class="op">×</button>
<button type="button" data-k="4">4</button><button type="button" data-k="5">5</button><button type="button" data-k="6">6</button><button type="button" data-k="-" class="op">−</button>
<button type="button" data-k="1">1</button><button type="button" data-k="2">2</button><button type="button" data-k="3">3</button><button type="button" data-k="+" class="op">+</button>
<button type="button" data-k="0">0</button><button type="button" data-k=".">.</button><button type="button" data-k="sqrt(" class="op">√</button><button type="button" data-k="^" class="op">^</button>
<button type="button" data-k="(">(</button><button type="button" data-k=")">)</button><button type="button" data-k="=" class="eq">=</button>
</div></div></div>
<div id="st-tip" role="dialog"></div>
<div id="st-toast" role="status"></div>
"""

JS_TEMPLATE = r"""
(function(){
"use strict";
if(window.__ST_V1)return;window.__ST_V1=1;
var PAGE=(function(){try{var p=location.pathname.split('/').filter(Boolean);return p.slice(-2).join('/')||'page';}catch(e){return 'page';}})();
var mem={};
var LS={g:function(k){try{var v=localStorage.getItem('st:'+PAGE+':'+k);return v==null?(k in mem?mem[k]:null):v;}catch(e){return(k in mem?mem[k]:null);}},s:function(k,v){mem[k]=v;try{localStorage.setItem('st:'+PAGE+':'+k,v);}catch(e){}},d:function(k){delete mem[k];try{localStorage.removeItem('st:'+PAGE+':'+k);}catch(e){}}};
function $(id){return document.getElementById(id);}
function toast(m){var t=$('st-toast');if(!t)return;t.textContent=m;t.style.display='block';clearTimeout(t._h);t._h=setTimeout(function(){t.style.display='none';},2200);}
function on(el,ev,fn){if(el)el.addEventListener(ev,fn);}
/* ---------- toolbar ---------- */
function setBar(v){$('st-bar').style.display=v?'flex':'none';$('st-show').style.display=v?'none':'block';}
function togglePanel(id){var p=$(id),was=p.classList.contains('open');closePanels();if(!was)p.classList.add('open');}
function closePanels(){Array.prototype.forEach.call(document.querySelectorAll('.st-p.open'),function(p){p.classList.remove('open');});}
on(document,'click',function(e){
  var c=e.target.closest('[data-close]');if(c){var p=$(c.getAttribute('data-close'));if(p)p.classList.remove('open');return;}
  var b=e.target.closest('#st-bar [data-act]');
  if(b){act(b.getAttribute('data-act'),b);return;}
  if(e.target.closest && e.target.closest('#st-show')){setBar(true);return;}
  var nb=e.target.closest && e.target.closest('[data-act="notes-copy"],[data-act="notes-clear"],[data-act="pen-clear"]');
  if(nb){act(nb.getAttribute('data-act'),nb);return;}
});
function act(a,btn){
  if(a==='hide'){setBar(false);return;}
  if(a==='pen'){penToggle(btn);return;}
  if(a==='hl'){applyHL();return;}
  if(a==='notes'){togglePanel('st-p-notes');var t=$('st-notes-area');if(t)setTimeout(function(){t.focus();},50);return;}
  if(a==='calc'){togglePanel('st-calc-p');return;}
  if(a==='words'){wordsToggle(btn);return;}
  if(a==='clear'){if(confirm('Clear pen drawings and highlights on this page?')){pen.paths=[];penSave();redrawPen();clearHL();toast('Cleared ✓');}return;}
  if(a==='pen-clear'){pen.paths=[];penSave();redrawPen();toast('Drawings cleared');return;}
  if(a==='notes-copy'){var t=$('st-notes-area');var v=t.value;function done(){toast('Notes copied ✓');}if(navigator.clipboard&&navigator.clipboard.writeText){navigator.clipboard.writeText(v).then(done,function(){fallback();});}else fallback();function fallback(){t.select();try{document.execCommand('copy');done();}catch(e){toast('Copy failed');}}return;}
  if(a==='notes-clear'){if(confirm('Delete your notes on this page?')){$('st-notes-area').value='';notesSave();}return;}
}
/* ---------- pen ---------- */
var pen={on:false,color:'#1d4ed8',w:4,er:false,paths:[],drawing:false};
var cv=null,ctx=null;
function docSize(){return{w:Math.max(document.documentElement.scrollWidth,window.innerWidth||0),h:Math.max(document.documentElement.scrollHeight,window.innerHeight||0)};}
function penInit(){cv=$('st-canvas');sizePen();var rT;on(window,'resize',function(){clearTimeout(rT);rT=setTimeout(sizePen,200);});penLoad();
  cv.addEventListener('pointerdown',function(e){if(!pen.on)return;e.preventDefault();try{cv.setPointerCapture(e.pointerId);}catch(x){}pen.drawing=true;var d=docSize();pen.cur={c:pen.color,w:pen.w,e:pen.er,p:[[ (e.clientX+window.scrollX)/d.w,(e.clientY+window.scrollY)/d.h]]};});
  cv.addEventListener('pointermove',function(e){if(!pen.on||!pen.drawing||!pen.cur)return;e.preventDefault();var d=docSize();var p=pen.cur.p;p.push([(e.clientX+window.scrollX)/d.w,(e.clientY+window.scrollY)/d.h]);if(p.length>1){var a=p[p.length-2],b=p[p.length-1];ctx.save();ctx.strokeStyle=pen.cur.c;ctx.lineWidth=pen.cur.w;ctx.lineCap='round';if(pen.cur.e)ctx.globalCompositeOperation='destination-out';ctx.beginPath();ctx.moveTo(a[0]*d.w,a[1]*d.h);ctx.lineTo(b[0]*d.w,b[1]*d.h);ctx.stroke();ctx.restore();}});
  function end(e){if(!pen.drawing)return;pen.drawing=false;if(pen.cur&&pen.cur.p.length){pen.paths.push(pen.cur);if(pen.paths.length>400)pen.paths.splice(0,pen.paths.length-400);penSave();}pen.cur=null;}
  cv.addEventListener('pointerup',end);cv.addEventListener('pointercancel',end);
}
function sizePen(){var d=docSize(),r=window.devicePixelRatio||1;cv.width=Math.round(d.w*r);cv.height=Math.round(d.h*r);cv.style.width=d.w+'px';cv.style.height=d.h+'px';ctx=cv.getContext('2d');ctx.setTransform(r,0,0,r,0,0);redrawPen();}
function redrawPen(){if(!ctx)return;var d=docSize();ctx.clearRect(0,0,d.w,d.h);pen.paths.forEach(function(p){ctx.save();ctx.strokeStyle=p.c;ctx.lineWidth=p.w;ctx.lineCap='round';ctx.lineJoin='round';if(p.e)ctx.globalCompositeOperation='destination-out';ctx.beginPath();p.p.forEach(function(pt,i){var x=pt[0]*d.w,y=pt[1]*d.h;if(i)ctx.lineTo(x,y);else ctx.moveTo(x,y);});ctx.stroke();ctx.restore();});}
function penSave(){try{LS.s('pen',JSON.stringify(pen.paths));}catch(e){toast('Too many strokes to save — kept for this visit');}}
function penLoad(){try{var v=LS.g('pen');if(!v)return;var a=JSON.parse(v);if(Object.prototype.toString.call(a)==='[object Array]'){pen.paths=a.filter(function(p){return p&&Object.prototype.toString.call(p.p)==='[object Array]';}).slice(-400);redrawPen();}}catch(e){}}
function penToggle(btn){pen.on=!pen.on;btn.classList.toggle('st-on',pen.on);cv.style.pointerEvents=pen.on?'auto':'none';if(pen.on){togglePanel('st-p-pen');toast('Pen on — draw anywhere');}else{closePanels();}}
on(document,'click',function(e){var s=e.target.closest&&e.target.closest('#st-swatches .st-sw');if(s){pen.color=s.getAttribute('data-c');pen.er=false;var er=document.querySelector('#st-swatches [data-er]');if(er)er.classList.remove('st-on');Array.prototype.forEach.call(document.querySelectorAll('#st-swatches .st-sw'),function(x){x.classList.remove('sel');});s.classList.add('sel');return;}var w=e.target.closest&&e.target.closest('#st-swatches [data-w]');if(w){pen.w=parseInt(w.getAttribute('data-w'),10)||4;return;}var er2=e.target.closest&&e.target.closest('#st-swatches [data-er]');if(er2){pen.er=!pen.er;er2.classList.toggle('st-on',pen.er);return;}});
/* ---------- highlight ---------- */
function tNodes(root){var o=[];try{var w=document.createTreeWalker(root,NodeFilter.SHOW_TEXT,{acceptNode:function(n){var p=n.parentElement;if(!p)return NodeFilter.REJECT;var t=p.tagName;if(t==='SCRIPT'||t==='STYLE'||t==='TEXTAREA'||t==='NOSCRIPT'||t==='SELECT'||t==='OPTION')return NodeFilter.REJECT;if(p.closest('#st-bar,#st-show,.st-p,#st-tip,#st-toast'))return NodeFilter.REJECT;if(!n.data.trim())return NodeFilter.REJECT;return NodeFilter.ACCEPT;}});while(w.nextNode())o.push(w.currentNode);}catch(e){}return o;}
function applyHL(){var s=null;try{s=window.getSelection();}catch(e){}if(!s||s.isCollapsed||!s.rangeCount){toast('Select some text first, then tap Highlight');return;}var r=s.getRangeAt(0);try{if($('st-bar').contains(r.commonAncestorContainer)){toast('Cannot highlight the toolbar');return;}}catch(e){}var sp=document.createElement('span');sp.className='st-hl';try{r.surroundContents(sp);}catch(e){try{sp.appendChild(r.extractContents());r.insertNode(sp);}catch(e2){toast('Could not highlight here');return;}}try{s.removeAllRanges();}catch(e){}saveHL();toast('Highlighted ✓');}
function saveHL(){var els=document.querySelectorAll('.st-hl');var seen={};var data=Array.prototype.map.call(els,function(el){var ex=el.textContent;var key=ex.slice(0,60);var o=seen[key]||0;seen[key]=o+1;var rb=document.createRange();rb.selectNodeContents(document.body);try{rb.setEnd(el,0);}catch(e){}var pre='';try{pre=rb.toString().slice(-48);}catch(e){}var ra=document.createRange();ra.selectNodeContents(document.body);try{ra.setStart(el,el.childNodes.length);}catch(e){}var suf='';try{suf=ra.toString().slice(0,48);}catch(e){}return{e:ex.slice(0,140),p:pre,s:suf,o:o};});try{LS.s('hl',JSON.stringify(data));}catch(e){}}
function clearHL(){Array.prototype.forEach.call(document.querySelectorAll('.st-hl'),function(el){var p=el.parentNode;while(el.firstChild)p.insertBefore(el.firstChild,el);p.removeChild(el);});try{document.body.normalize();}catch(e){}LS.d('hl');}
function nodeMap(nodes){var map=[],off=0;nodes.forEach(function(n){map.push({node:n,start:off,end:off+n.data.length});off+=n.data.length;});return{map:map,full:nodes.map(function(n){return n.data;}).join('')};}
function offToNode(map,off){for(var i=0;i<map.length;i++){if(off<=map[i].end)return{node:map[i].node,off:Math.min(off-map[i].start,map[i].node.data.length)};}var l=map[map.length-1];return{node:l.node,off:l.node.data.length};}
function wrapRange(r){var sp=document.createElement('span');sp.className='st-hl';try{r.surroundContents(sp);}catch(e){try{sp.appendChild(r.extractContents());r.insertNode(sp);}catch(e2){}}}
function restoreHL(){var raw=LS.g('hl');if(!raw)return;var data;try{data=JSON.parse(raw);}catch(e){return;}if(!Object.prototype.toString.call(data)==='[object Array]'&&!Array.isArray(data))return;var ranges=[];data.forEach(function(a){if(!a||!a.e)return;try{var nm=nodeMap(tNodes(document.body));var idxs=[],pos=-1;while(true){pos=nm.full.indexOf(a.e,pos+1);if(pos<0)break;var okP=!a.p||nm.full.slice(Math.max(0,pos-a.p.length),pos)===a.p;var okS=!a.s||nm.full.slice(pos+a.e.length,pos+a.e.length+a.s.length)===a.s;if(okP&&okS)idxs.push(pos);}var at=idxs.length>1?idxs[Math.min(a.o||0,idxs.length-1)]:(idxs[0]!=null?idxs[0]:nm.full.indexOf(a.e));if(at==null||at<0)return;var s=offToNode(nm.map,at),t=offToNode(nm.map,at+a.e.length);var r=document.createRange();r.setStart(s.node,s.off);r.setEnd(t.node,t.off);ranges.push({at:at,r:r});}catch(e){}});ranges.sort(function(x,y){return y.at-x.at;}).forEach(function(x){wrapRange(x.r);});}
/* ---------- notes ---------- */
var notesT=null;
function notesLoad(){var t=$('st-notes-area');if(!t)return;try{t.value=LS.g('notes')||'';}catch(e){}notesMeta();}
function notesSave(){var t=$('st-notes-area');if(!t)return;try{LS.s('notes',t.value);}catch(e){}notesMeta();}
function notesMeta(){var t=$('st-notes-area'),m=$('st-notes-meta');if(!t||!m)return;var v=t.value.trim();var w=v?v.split(/\s+/).length:0;m.textContent=w+' words • saved on this device';}
function notesInit(){var t=$('st-notes-area');if(!t)return;notesLoad();t.addEventListener('input',function(){clearTimeout(notesT);notesT=setTimeout(notesSave,400);});}
/* ---------- calculator ---------- */
var calcExpr='',calcFresh=true;
function calcShow(v){$('st-calc-disp').textContent=v;}
function calcPress(k){
  if(k==='C'){calcExpr='';calcFresh=true;$('st-calc-hist').textContent='';calcShow('0');return;}
  if(k==='bk'){calcExpr=calcExpr.slice(0,-1);calcShow(pretty(calcExpr)||'0');return;}
  if(k==='='){if(!calcExpr)return;try{var r=calcEval(calcExpr);$('st-calc-hist').textContent=pretty(calcExpr)+' =';calcShow(String(r));calcExpr=String(r);calcFresh=true;}catch(e){calcShow('Error');calcExpr='';calcFresh=true;}return;}
  if(calcFresh&&/[0-9.(]/.test(k)){calcExpr='';calcFresh=false;}
  if(calcFresh&&/[+\-*/%^]/.test(k)){calcFresh=false;}
  calcExpr+=k;calcShow(pretty(calcExpr));
}
function pretty(s){return String(s).replace(/\*/g,'×').replace(/\//g,'÷').replace(/-/g,'−').replace(/sqrt\(/g,'√(');}
function calcEval(s){s=String(s).replace(/(\d+(?:\.\d+)?)%/g,'($1/100)').replace(/√\(/g,'Math.sqrt(').replace(/\^/g,'**');var t=s.replace(/Math\.sqrt/g,'');if(!t||/[^0-9+\-*/().%\s]/.test(t))throw new Error('bad');var r=Function('"use strict";return('+s+')')();if(typeof r!=='number'||!isFinite(r))throw new Error('bad');return Math.round(r*1e10)/1e10;}
function calcInit(){on($('st-calc-grid'),'click',function(e){var b=e.target.closest&&e.target.closest('[data-k]');if(b)calcPress(b.getAttribute('data-k'));});
  document.addEventListener('keydown',function(e){var p=$('st-calc-p');if(!p||!p.classList.contains('open'))return;var t=e.target;if(t&&(t.tagName==='TEXTAREA'||t.tagName==='INPUT'))return;var k=e.key;if(/^[0-9+\-*/%^().%]$/.test(k)){calcPress(k);}else if(k==='Enter'){e.preventDefault();calcPress('=');}else if(k==='Backspace'){calcPress('bk');}else if(k==='Escape'){p.classList.remove('open');}});
  (function(){var h=$('st-calc-head'),p=$('st-calc-p');if(!h||!p)return;var sx,sy,sl,st,drag=false;h.addEventListener('pointerdown',function(e){if(e.target.closest('[data-close]'))return;drag=true;sx=e.clientX;sy=e.clientY;var r=p.getBoundingClientRect();sl=r.left;st=r.top;p.style.left=sl+'px';p.style.top=st+'px';p.style.right='auto';try{h.setPointerCapture(e.pointerId);}catch(x){}});h.addEventListener('pointermove',function(e){if(!drag)return;p.style.left=(sl+e.clientX-sx)+'px';p.style.top=Math.max(8,st+e.clientY-sy)+'px';});h.addEventListener('pointerup',function(){drag=false;});h.addEventListener('pointercancel',function(){drag=false;});})();
}
/* ---------- vocabulary ---------- */
var VOCAB=__VOCAB_JSON__;
var WORD_RE=null,wordCount={};
function buildRE(){var ks=Object.keys(VOCAB).sort(function(a,b){return b.length-a.length;});var esc=ks.map(function(k){return k.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');});WORD_RE=new RegExp('\\b('+esc.join('|')+')(s?)\\b','gi');}
function wordsOn(){wordCount={};if(!WORD_RE)buildRE();tNodes(document.body).forEach(function(t){var m,last=0,frag=null;WORD_RE.lastIndex=0;while((m=WORD_RE.exec(t.data))){var key=m[1].toLowerCase();if(!(key in VOCAB))continue;wordCount[key]=wordCount[key]||0;if(wordCount[key]>=2)continue;wordCount[key]++;if(!frag)frag=document.createDocumentFragment();frag.appendChild(document.createTextNode(t.data.slice(last,m.index)));var b=document.createElement('button');b.type='button';b.className='st-vocab';b.setAttribute('data-w',key);b.setAttribute('title','Show meaning');b.textContent=m[0];frag.appendChild(b);last=m.index+m[0].length;}if(frag){frag.appendChild(document.createTextNode(t.data.slice(last)));try{t.parentNode.replaceChild(frag,t);}catch(e){}}});}
function wordsOff(){Array.prototype.forEach.call(document.querySelectorAll('.st-vocab'),function(b){try{b.parentNode.replaceChild(document.createTextNode(b.textContent),b);}catch(e){}});wordCount={};hideTip();}
function wordsToggle(btn){var on=btn.classList.contains('st-on');if(on){btn.classList.remove('st-on');wordsOff();try{LS.s('words','0');}catch(e){}}else{btn.classList.add('st-on');wordsOn();try{LS.s('words','1');}catch(e){}toast('Tap a dotted word for its meaning');}}
function showTip(btn){var w=btn.getAttribute('data-w');var v=VOCAB[w];if(!v)return;var tip=$('st-tip');tip.innerHTML='';var b=document.createElement('b');b.textContent=btn.textContent+' • '+v.p;tip.appendChild(b);tip.appendChild(document.createElement('br'));tip.appendChild(document.createTextNode(v.d));tip.style.display='block';var r=btn.getBoundingClientRect();var tw=Math.min(300,window.innerWidth*0.86);var x=Math.min(Math.max(8,r.left),window.innerWidth-tw-8);var y=r.bottom+8;if(y+90>window.innerHeight)y=Math.max(8,r.top-100);tip.style.left=x+'px';tip.style.top=y+'px';}
function hideTip(){var tip=$('st-tip');if(tip)tip.style.display='none';}
on(document,'click',function(e){var v=e.target.closest&&e.target.closest('.st-vocab');if(v){e.stopPropagation();showTip(v);return;}if(!(e.target.closest&&e.target.closest('#st-tip')))hideTip();});
document.addEventListener('keydown',function(e){if(e.key==='Escape'){hideTip();closePanels();}});
/* ---------- init ---------- */
penInit();notesInit();calcInit();
try{if(LS.g('words')==='1'){var wb=document.querySelector('#st-bar [data-act="words"]');if(wb)wb.classList.add('st-on');wordsOn();}}catch(e){}
restoreHL();
})();
"""

HTML_DOC_CLOSE = "</body>"


def build_snippet():
    """Return the full HTML snippet (style + toolbar + script)."""
    vocab_json = json.dumps({w: {"p": p, "d": d} for w, (p, d) in VOCAB.items()}, ensure_ascii=False)
    js = JS_TEMPLATE.replace("__VOCAB_JSON__", vocab_json)
    return (
        MARKER + "\n<style>\n" + CSS + "\n</style>\n" + HTML + "\n<script>\n" + js + "\n</script>"
    )


def inject(html_text):
    """Insert the snippet before </body>. Returns (new_html, changed)."""
    if MARKER in html_text:
        return html_text, False
    snippet = build_snippet()
    lower = html_text.lower()
    idx = lower.rfind(HTML_DOC_CLOSE)
    if idx == -1:
        return html_text + "\n" + snippet + "\n", True
    return html_text[:idx] + snippet + "\n" + html_text[idx:], True


def extract_js():
    """Return just the JS (with real vocab) for `node --check` validation."""
    vocab_json = json.dumps({w: {"p": p, "d": d} for w, (p, d) in VOCAB.items()}, ensure_ascii=False)
    return JS_TEMPLATE.replace("__VOCAB_JSON__", vocab_json)
