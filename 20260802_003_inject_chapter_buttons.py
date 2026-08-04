#!/usr/bin/env python3
"""
20260802_003_inject_chapter_buttons.py
Add per-chapter action buttons to a Romans Road Commentary HTML volume.

Each chapter gets wrapped in:
  <div class="chapter-block" id="block-chapter-N">
    <div class="chapter-content"> ... all chapter text ... </div>
    <div class="doc-actions"> ... vertical button column ... </div>
  </div>

The button column sits to the right of the chapter text, sticky, starting
at the chapter title. Five buttons: PDF, Link, Copy, HTML, Embed.

Usage:
    python3 20260802_003_inject_chapter_buttons.py input.html output.html

Idempotent: skips if chapter buttons are already present.
"""

import re
import sys

# ── CSS ───────────────────────────────────────────────────────────────────────
CHAPTER_BTN_CSS = """
<style>
/* Per-chapter layout: content left, button column right */
.chapter-block {
  display: flex;
  flex-direction: row;
  align-items: flex-start;
}
.chapter-content {
  flex: 1;
  min-width: 0;
}
.doc-actions {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 0.75rem 0.5rem;
  background: transparent;
  border-left: 1px solid rgba(184,151,58,0.2);
  margin-left: 1rem;
  position: sticky;
  top: 4rem;
  align-self: flex-start;
  width: auto;
}
.doc-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.4rem;
  background: transparent;
  border: 1px solid rgba(184,151,58,0.4);
  border-radius: 3px;
  color: rgba(244,236,216,0.75);
  cursor: pointer;
  white-space: nowrap;
}
.doc-btn:hover {
  border-color: var(--gold, #b8973a);
  color: var(--gold, #b8973a);
  background: rgba(184,151,58,0.08);
}
.doc-btn svg { width: 16px; height: 16px; flex-shrink: 0; }
@media print {
  #sidebar, #progress-bar, #menu-toggle, #sidebar-overlay,
  .verse-tooltip, .doc-actions { display: none !important; }
  .chapter-block { display: block !important; }
  .chapter-content { display: block !important; }
}
</style>"""

# ── Toast + JS ────────────────────────────────────────────────────────────────
CHAPTER_BTN_JS = r"""
<div id="docToast" style="display:none;position:fixed;bottom:1.5rem;right:1.5rem;background:var(--ink,#1a1410);color:var(--parchment,#f5f0e8);border:1px solid var(--gold,#b8973a);padding:0.6rem 1rem;font-family:'Cinzel',serif;font-size:0.72rem;letter-spacing:0.08em;z-index:10000;border-radius:3px;pointer-events:none;"></div>
<script>
function showToast(msg) {
  var t = document.getElementById('docToast');
  t.textContent = msg; t.style.display = 'block';
  setTimeout(function() { t.style.display = 'none'; }, 2200);
}
function docChapterAction(type, id) {
  var block = document.getElementById('block-' + id);
  var url = location.origin + location.pathname + '#' + id;
  switch (type) {
    case 'link':
      navigator.clipboard.writeText(url)
        .then(function() { showToast('Chapter link copied'); });
      break;
    case 'embed':
      navigator.clipboard.writeText('<iframe src="' + url + '" width="100%" height="600" frameborder="0"></iframe>')
        .then(function() { showToast('Embed code copied'); });
      break;
    case 'clipboard':
      var content = block ? block.querySelector('.chapter-content') : null;
      navigator.clipboard.writeText(content ? content.innerText : '')
        .then(function() { showToast('Chapter text copied'); });
      break;
    case 'html':
      var content2 = block ? block.querySelector('.chapter-content') : null;
      navigator.clipboard.writeText(content2 ? content2.innerHTML : '')
        .then(function() { showToast('Chapter HTML copied'); });
      break;
    case 'pdf':
      if (block) {
        document.querySelectorAll('.chapter-block').forEach(function(b) {
          b.style.display = (b === block) ? '' : 'none';
        });
        // Defer print until browser has repainted with hidden blocks
        requestAnimationFrame(function() {
          requestAnimationFrame(function() {
            window.print();
            document.querySelectorAll('.chapter-block').forEach(function(b) {
              b.style.display = '';
            });
          });
        });
      } else {
        window.print();
      }
      break;
  }
}
</script>"""

# ── Button column HTML (Phosphor SVG icons, icon-only, title for tooltip) ────
def make_buttons(chapter_id):
    cid = chapter_id
    return (
        '<div class="doc-actions">\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'pdf\',\'{cid}\')" title="Print chapter as PDF"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M224,152a8,8,0,0,1-8,8H192v16h16a8,8,0,0,1,0,16H192v16a8,8,0,0,1-16,0V152a8,8,0,0,1,8-8h32A8,8,0,0,1,224,152ZM92,172a28,28,0,0,1-28,28H56v8a8,8,0,0,1-16,0V152a8,8,0,0,1,8-8H64A28,28,0,0,1,92,172Zm-16,0a12,12,0,0,0-12-12H56v24h8A12,12,0,0,0,76,172Zm88,8a36,36,0,0,1-36,36H112a8,8,0,0,1-8-8V152a8,8,0,0,1,8-8h16A36,36,0,0,1,164,180Zm-16,0a20,20,0,0,0-20-20h-8v40h8A20,20,0,0,0,148,180ZM40,116V40A16,16,0,0,1,56,24h96a8,8,0,0,1,5.66,2.34l56,56A8,8,0,0,1,216,88v28a8,8,0,0,1-16,0V96H152a8,8,0,0,1-8-8V40H56v76a8,8,0,0,1-16,0ZM160,80h28.69L160,51.31Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'link\',\'{cid}\')" title="Copy chapter link"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M137.54,186.36a8,8,0,0,1,0,11.31l-9.94,10A56,56,0,0,1,48.38,128.4L72.5,104.28A56,56,0,0,1,149.31,102a8,8,0,1,1-10.64,12,40,40,0,0,0-54.85,1.63L59.7,139.72a40,40,0,1,0,56.58,56.58l9.94-9.94A8,8,0,0,1,137.54,186.36Zm70.08-138a56.08,56.08,0,0,0-79.22,0l-9.94,9.95a8,8,0,0,0,11.32,11.31l9.94-9.94a40,40,0,1,1,56.58,56.58L172.18,140.4A40,40,0,0,1,117.33,142a8,8,0,0,0-10.64,12,56,56,0,0,0,76.81-2.26l24.12-24.12A56.08,56.08,0,0,0,207.62,48.38Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'clipboard\',\'{cid}\')" title="Copy chapter text"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M165.66,2.34a8,8,0,0,0-11.32,0L136,20.69l-6.34-6.35a8,8,0,0,0-11.32,11.32L128,35.31l-96,96V224a8,8,0,0,0,8,8H232a8,8,0,0,0,8-8V131.31Zm-128,201,75.51-75.51,18.34,18.34L56,221.37ZM224,216H179.31l-30.62-30.63,18.34-18.34L224,224Zm0-42.63-82.34-82.34,16-16L224,151.37ZM152,69,51.31,169.66,40,158.34,140.69,57.66ZM165.66,56,144,77.66,139.31,73l21.66-21.65Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'html\',\'{cid}\')" title="Copy chapter HTML"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M216,88H152V40a8,8,0,0,0-8-8H56A16,16,0,0,0,40,48V208a16,16,0,0,0,16,16H200a16,16,0,0,0,16-16V96A8,8,0,0,0,216,88Zm-56,0V51.31L208.69,88ZM56,208V48h80V96a8,8,0,0,0,8,8h56V208Zm130.34-82.34a8,8,0,0,1,0,11.31L165.66,158l20.68,20.69a8,8,0,0,1-11.32,11.31l-26.34-26.34a8,8,0,0,1,0-11.32l26.34-26.34A8,8,0,0,1,186.34,125.66Zm-96,11.31L110.34,158,89.66,178.69A8,8,0,0,1,78.34,167.38L99,146.66,78.34,126a8,8,0,1,1,11.32-11.31Z"/></svg></button>\n'
        f'  <button class="doc-btn" onclick="docChapterAction(\'embed\',\'{cid}\')" title="Embed code"><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 256 256" fill="currentColor"><path d="M69.12,94.15,28.5,128l40.62,33.85a8,8,0,1,1-10.24,12.29l-48-40a8,8,0,0,1,0-12.29l48-40a8,8,0,0,1,10.24,12.3Zm176,27.7-48-40a8,8,0,1,0-10.24,12.3L227.5,128l-40.62,33.85a8,8,0,1,0,10.24,12.29l48-40a8,8,0,0,0,0-12.29ZM162.73,32.48a8,8,0,0,0-10.25,4.79l-64,176a8,8,0,0,0,4.79,10.26A8.14,8.14,0,0,0,96,224a8,8,0,0,0,7.52-5.27l64-176A8,8,0,0,0,162.73,32.48Z"/></svg></button>\n'
        '</div>'
    )


# ── Regex: matches any <h1> with id="chapter-N" ───────────────────────────────
CHAPTER_H1_RE = re.compile(r'(<h1\b[^>]*\bid="(chapter-\d+)"[^>]*>)')


def inject(html, force=False):
    """Wrap chapters, place button column to the right, add CSS/JS."""

    if not force and 'docChapterAction' in html:
        return html, 0

    # ── Wrap chapters ─────────────────────────────────────────────────────────
    # Each chapter becomes:
    #   <div class="chapter-block" id="block-chapter-N">
    #     <div class="chapter-content"> [all chapter text] </div>
    #     <div class="doc-actions"> [buttons] </div>
    #   </div>
    #
    # We open chapter-block + chapter-content at the h1, and close them
    # (inserting the button column between) at the next h1 or end of body.

    first = [True]
    prev_id = [None]
    count = [0]

    def wrap_repl(m):
        chapter_id = m.group(2)
        block_id = 'block-' + chapter_id
        count[0] += 1

        if first[0]:
            first[0] = False
            prev_id[0] = chapter_id
            return (
                f'<div class="chapter-block" id="{block_id}">'
                f'<div class="chapter-content">'
                f'{m.group(1)}'
            )
        else:
            buttons = make_buttons(prev_id[0])
            prev_id[0] = chapter_id
            return (
                f'</div>\n{buttons}\n</div>\n'
                f'<div class="chapter-block" id="{block_id}">'
                f'<div class="chapter-content">'
                f'{m.group(1)}'
            )

    html = CHAPTER_H1_RE.sub(wrap_repl, html)

    if count[0] == 0:
        return html, 0

    # Close the last chapter before </body>
    if prev_id[0]:
        last_buttons = make_buttons(prev_id[0])
        body_close = html.rfind('</body>')
        if body_close != -1:
            html = html[:body_close] + f'</div>\n{last_buttons}\n</div>\n' + html[body_close:]

    # ── CSS before </head> ────────────────────────────────────────────────────
    head_close = html.rfind('</head>')
    if head_close != -1:
        html = html[:head_close] + CHAPTER_BTN_CSS + '\n' + html[head_close:]

    # ── Toast + JS before </body> ─────────────────────────────────────────────
    body_close = html.rfind('</body>')
    if body_close != -1:
        html = html[:body_close] + CHAPTER_BTN_JS + '\n' + html[body_close:]

    return html, count[0]


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    infile, outfile = sys.argv[1], sys.argv[2]
    force = '--force' in sys.argv

    with open(infile, encoding='utf-8') as f:
        html = f.read()

    result, count = inject(html, force=force)

    if count == 0:
        if 'docChapterAction' in result:
            print(f'Skipped — chapter buttons already present in {infile}')
        else:
            print(f'Warning: no chapter patterns matched in {infile}')
        return

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f'Done: {count} chapters wrapped and buttoned → {outfile}')


if __name__ == '__main__':
    main()
