#!/usr/bin/env python3
"""
20260802_004_volume_pipeline.py
Full processing pipeline for a Romans Road Commentary volume.

Input:  ESV-linked volume (output of 20260802_001_add_esv_links.py)
Output: Finished volume with tooltip + per-chapter buttons

Buttons float right of chapter text, stacked vertically, no structural
wrappers added. Five buttons per chapter: PDF, Link, Copy, HTML, Embed.

PDF scoping: hides all non-chapter body children, prints, restores.

Usage:
    python3 20260802_004_volume_pipeline.py Romans_Road_linked.html Romans_Road_v2.html
"""

import re, sys

# ── ESV tooltip ───────────────────────────────────────────────────────────────
TOOLTIP_CSS = """
<style>
.verse-tooltip {
  position: fixed; z-index: 9999;
  background: var(--ink, #1c140a); color: var(--parchment, #f5f0e8);
  border: 1px solid var(--gold, #b8963e); border-radius: 4px;
  padding: 0.75rem 1rem; font-size: 0.88rem; line-height: 1.6;
  max-width: 420px; box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  display: none; pointer-events: none;
}
.verse-tooltip-reference {
  font-family: 'Cinzel', serif; font-size: 0.72rem;
  letter-spacing: 0.1em; color: var(--gold, #b8963e);
  margin-bottom: 0.4rem; text-transform: uppercase;
}
</style>"""

TOOLTIP_BLOCK = r"""<div class="verse-tooltip" id="verseTooltip"></div>
<script>
(function() {
  const PROXY = 'https://esv-proxy.johndwilbourn.workers.dev';
  const CACHE = {};
  const tooltip = document.getElementById('verseTooltip');
  async function fetchVerse(ref) {
    if (CACHE[ref]) return CACHE[ref];
    try {
      const res = await fetch(PROXY + '?q=' + encodeURIComponent(ref));
      const data = await res.json();
      const text = (data.passages && data.passages[0]) ? data.passages[0].trim() : 'Could not load verse.';
      CACHE[ref] = text; return text;
    } catch(e) { return 'Could not load verse.'; }
  }
  function show(e, ref, display) {
    tooltip.innerHTML = '<div class="verse-tooltip-reference">' + display + '</div>Loading\u2026';
    tooltip.style.display = 'block'; position(e);
    fetchVerse(ref).then(t => {
      tooltip.innerHTML = '<div class="verse-tooltip-reference">' + display + '</div>' + t;
    });
  }
  function position(e) {
    const m = 14; let x = e.clientX + m, y = e.clientY + m;
    if (x + 440 > window.innerWidth)  x = e.clientX - 440 - m;
    if (y + 180 > window.innerHeight) y = e.clientY - 180 - m;
    tooltip.style.left = x + 'px'; tooltip.style.top = y + 'px';
  }
  document.querySelectorAll('a[href*="esv.org"]').forEach(a => {
    const display = a.textContent.trim();
    const ref = decodeURIComponent(a.getAttribute('href').replace('https://www.esv.org/', '').replace(/\+/g, ' '));
    a.addEventListener('mouseenter', e => show(e, ref, display));
    a.addEventListener('mousemove', position);
    a.addEventListener('mouseleave', () => { tooltip.style.display = 'none'; });
  });
})();
</script>"""

# ── Chapter buttons ───────────────────────────────────────────────────────────
CHAPTER_BTN_CSS = """
<style>
/* Per-chapter action buttons — float right of chapter text */
.doc-actions {
  float: right;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin: 0 0 1rem 1.5rem;
  padding: 0.5rem;
  border-left: 1px solid rgba(184,151,58,0.25);
  clear: right;
}
.doc-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem;
  background: transparent;
  border: 1px solid rgba(184,151,58,0.4);
  border-radius: 3px;
  color: var(--gold, #b8963e);
  cursor: pointer;
}
.doc-btn:hover {
  border-color: var(--gold, #b8973a);
  color: var(--ink, #1a1410);
  background: var(--gold, #b8963e);
}
.doc-btn svg { width: 16px; height: 16px; display: block; }
@media print {
  body[data-printing] > * { display: none !important; }
  body[data-printing] > .chapter-print-target { display: block !important; }
  .doc-actions, #sidebar, #progress-bar, #menu-toggle,
  #sidebar-overlay, .verse-tooltip { display: none !important; }
}
</style>"""

CHAPTER_BTN_JS = r"""
<div id="docToast" style="display:none;position:fixed;bottom:1.5rem;right:1.5rem;
  background:var(--ink,#1a1410);color:var(--parchment,#f5f0e8);
  border:1px solid var(--gold,#b8973a);padding:0.6rem 1rem;
  font-family:'Cinzel',serif;font-size:0.72rem;letter-spacing:0.08em;
  z-index:10000;border-radius:3px;pointer-events:none;"></div>
<script>
function showToast(msg) {
  var t = document.getElementById('docToast');
  t.textContent = msg; t.style.display = 'block';
  setTimeout(function() { t.style.display = 'none'; }, 2200);
}
function getChapterNodes(id) {
  var h = document.getElementById(id);
  if (!h) return [];
  var nodes = [h], el = h.nextElementSibling;
  while (el && !el.classList.contains('chapter-title')) {
    nodes.push(el); el = el.nextElementSibling;
  }
  return nodes;
}
function docChapterAction(type, id) {
  var url = location.origin + location.pathname + '#' + id;
  switch (type) {
    case 'link':
      navigator.clipboard.writeText(url)
        .then(function() { showToast('Chapter link copied'); });
      break;
    case 'embed':
      navigator.clipboard.writeText(
        '<iframe src="' + url + '" width="100%" height="600" frameborder="0"></iframe>'
      ).then(function() { showToast('Embed code copied'); });
      break;
    case 'clipboard':
      navigator.clipboard.writeText(
        getChapterNodes(id).map(function(n) { return n.innerText; }).join('\n').trim()
      ).then(function() { showToast('Chapter text copied'); });
      break;
    case 'html':
      navigator.clipboard.writeText(
        getChapterNodes(id).map(function(n) { return n.outerHTML; }).join('\n')
      ).then(function() { showToast('Chapter HTML copied'); });
      break;
    case 'pdf':
      var nodes = getChapterNodes(id);
      var chapterHTML = nodes.map(function(n) { return n.outerHTML; }).join('\n');
      var styles = Array.from(document.head.querySelectorAll('link[rel="stylesheet"]'))
        .map(function(el) { return '<link rel="stylesheet" href="' + el.href + '">'; }).join('\n');
      var inlineStyles = Array.from(document.head.querySelectorAll('style'))
        .map(function(el) { return el.outerHTML; }).join('\n');
      var win = window.open('', '_blank');
      if (!win) { showToast('Allow popups for PDF'); break; }
      var chapterNum = id.replace('chapter-', '');
      var titleBase = document.title.replace(/\s*[—–]\s*/g, ' - ').trim();
      var printTitle = titleBase + ' - Chapter ' + chapterNum;
      win.document.write('<!DOCTYPE html><html><head><meta charset="UTF-8"><title>' + printTitle + '</title>'
        + styles + inlineStyles + '</head><body>' + chapterHTML + '</body></html>');
      win.document.close();
      win.onload = function() { win.print(); };
      break;
  }
}
</script>"""

def make_buttons(chapter_id):
    cid = chapter_id
    return (
        '\n<div class="doc-actions">\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'pdf\',\'{cid}\')" title="Print chapter as PDF"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M224,152a8,8,0,0,1-8,8H192v16h16a8,8,0,0,1,0,16H192v16a8,8,0,0,1-16,0V152a8,8,0,0,1,8-8h32A8,8,0,0,1,224,152ZM92,172a28,28,0,0,1-28,28H56v8a8,8,0,0,1-16,0V152a8,8,0,0,1,8-8H64A28,28,0,0,1,92,172Zm-16,0a12,12,0,0,0-12-12H56v24h8A12,12,0,0,0,76,172Zm88,8a36,36,0,0,1-36,36H112a8,8,0,0,1-8-8V152a8,8,0,0,1,8-8h16A36,36,0,0,1,164,180Zm-16,0a20,20,0,0,0-20-20h-8v40h8A20,20,0,0,0,148,180ZM40,116V40A16,16,0,0,1,56,24h96a8,8,0,0,1,5.66,2.34l56,56A8,8,0,0,1,216,88v28a8,8,0,0,1-16,0V96H152a8,8,0,0,1-8-8V40H56v76a8,8,0,0,1-16,0ZM160,80h28.69L160,51.31Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'link\',\'{cid}\')" title="Copy chapter link"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M137.54,186.36a8,8,0,0,1,0,11.31l-9.94,10A56,56,0,0,1,48.38,128.4L72.5,104.28A56,56,0,0,1,149.31,102a8,8,0,1,1-10.64,12,40,40,0,0,0-54.85,1.63L59.7,139.72a40,40,0,1,0,56.58,56.58l9.94-9.94A8,8,0,0,1,137.54,186.36Zm70.08-138a56.08,56.08,0,0,0-79.22,0l-9.94,9.95a8,8,0,0,0,11.32,11.31l9.94-9.94a40,40,0,1,1,56.58,56.58L172.18,140.4A40,40,0,0,1,117.33,142a8,8,0,0,0-10.64,12,56,56,0,0,0,76.81-2.26l24.12-24.12A56.08,56.08,0,0,0,207.62,48.38Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'clipboard\',\'{cid}\')" title="Copy chapter text"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M165.66,2.34a8,8,0,0,0-11.32,0L136,20.69l-6.34-6.35a8,8,0,0,0-11.32,11.32L128,35.31l-96,96V224a8,8,0,0,0,8,8H232a8,8,0,0,0,8-8V131.31Zm-128,201,75.51-75.51,18.34,18.34L56,221.37ZM224,216H179.31l-30.62-30.63,18.34-18.34L224,224Zm0-42.63-82.34-82.34,16-16L224,151.37ZM152,69,51.31,169.66,40,158.34,140.69,57.66ZM165.66,56,144,77.66,139.31,73l21.66-21.65Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'html\',\'{cid}\')" title="Copy chapter HTML"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M216,88H152V40a8,8,0,0,0-8-8H56A16,16,0,0,0,40,48V208a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V96A8,8,0,0,0,216,88Zm-56,0V51.31L208.69,88ZM56,208V48h80V96a8,8,0,0,0,8,8h56V208Zm130.34-82.34a8,8,0,0,1,0,11.31L165.66,158l20.68,20.69a8,8,0,0,1-11.32,11.31l-26.34-26.34a8,8,0,0,1,0-11.32l26.34-26.34A8,8,0,0,1,186.34,125.66Zm-96,11.31L110.34,158,89.66,178.69A8,8,0,0,1,78.34,167.38L99,146.66,78.34,126a8,8,0,1,1,11.32-11.31Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'embed\',\'{cid}\')" title="Embed code"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,0,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26A8.14,8.14,0,0,0,96,224a8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z"/></svg></button>\n'
        '</div>\n'
    )

# Matches h1 (any attr order) + immediately following h2.chapter-subtitle
CHAPTER_BLOCK_RE = re.compile(
    r'(<h1\b[^>]*\bid="(chapter-\d+)"[^>]*>.*?</h1>'
    r'[ \t]*\n?[ \t]*'
    r'<h2\b[^>]*\bclass="chapter-subtitle"[^>]*>.*?</h2>)',
    re.DOTALL
)

def process(html):
    # ── Tooltip CSS → before </head> ─────────────────────────────────────────
    i = html.rfind('</head>')
    html = html[:i] + TOOLTIP_CSS + '\n' + html[i:]

    # ── Chapter button CSS → before </head> ──────────────────────────────────
    i = html.rfind('</head>')
    html = html[:i] + CHAPTER_BTN_CSS + '\n' + html[i:]

    # ── Chapter buttons → after each h1+h2 block ─────────────────────────────
    def btn_repl(m):
        return m.group(1) + make_buttons(m.group(2))
    html, count = CHAPTER_BLOCK_RE.subn(btn_repl, html)

    # ── Tooltip block + chapter JS → before </body> ───────────────────────────
    i = html.rfind('</body>')
    html = html[:i] + TOOLTIP_BLOCK + '\n' + CHAPTER_BTN_JS + '\n' + html[i:]

    return html, count

def main():
    if len(sys.argv) < 3:
        print(__doc__); sys.exit(1)
    infile, outfile = sys.argv[1], sys.argv[2]
    with open(infile, encoding='utf-8') as f:
        html = f.read()
    if 'docChapterAction' in html:
        print(f'Error: {infile} already has chapter buttons. Use the clean ESV-linked file as input.')
        sys.exit(1)
    result, count = process(html)
    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(result)
    print(f'Done: tooltip + {count} chapter button bars → {outfile}')

if __name__ == '__main__':
    main()
