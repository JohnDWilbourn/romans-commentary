#!/usr/bin/env python3
"""
20260802_002_inject_esv_tooltip.py
Inject the ESV hover-tooltip CSS, div, and JavaScript into a Romans Road volume.

Run AFTER 20260802_001_add_esv_links.py has added <a href="...esv.org..."> links.
Idempotent: skips the file if the tooltip div is already present.

Usage:
    python3 20260802_002_inject_esv_tooltip.py input.html output.html
"""

import sys

# ── CSS ───────────────────────────────────────────────────────────────────────
# Injected just before </head>.
# CSS variable fallbacks keep the tooltip readable even if --ink/--parchment/--gold
# aren't defined in this volume's style.css.
TOOLTIP_CSS = """
<style>
/* ESV verse hover tooltip */
.verse-tooltip {
  position: fixed;
  z-index: 9999;
  background: var(--ink, #1c140a);
  color: var(--parchment, #f5f0e8);
  border: 1px solid var(--gold, #b8963e);
  border-radius: 4px;
  padding: 0.75rem 1rem;
  font-size: 0.88rem;
  line-height: 1.6;
  max-width: 420px;
  box-shadow: 0 4px 12px rgba(0,0,0,0.3);
  display: none;
  pointer-events: none;
}
.verse-tooltip-reference {
  font-family: 'Cinzel', serif;
  font-size: 0.72rem;
  letter-spacing: 0.1em;
  color: var(--gold, #b8963e);
  margin-bottom: 0.4rem;
  text-transform: uppercase;
}
</style>"""

# ── Div + JS ──────────────────────────────────────────────────────────────────
# Injected just before </body>.
# Hooks into every <a href*="esv.org"> on the page — no per-link changes needed.
TOOLTIP_BLOCK = """<div class="verse-tooltip" id="verseTooltip"></div>
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
      CACHE[ref] = text;
      return text;
    } catch(e) { return 'Could not load verse.'; }
  }
  function show(e, ref, display) {
    tooltip.innerHTML = '<div class="verse-tooltip-reference">' + display + '</div>Loading\u2026';
    tooltip.style.display = 'block';
    position(e);
    fetchVerse(ref).then(t => {
      tooltip.innerHTML = '<div class="verse-tooltip-reference">' + display + '</div>' + t;
    });
  }
  function position(e) {
    const m = 14;
    let x = e.clientX + m, y = e.clientY + m;
    if (x + 440 > window.innerWidth) x = e.clientX - 440 - m;
    if (y + 180 > window.innerHeight) y = e.clientY - 180 - m;
    tooltip.style.left = x + 'px';
    tooltip.style.top = y + 'px';
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


def inject(html):
    """Add tooltip CSS and JS to html string. Returns (result, changed)."""

    # Idempotency: don't double-inject
    if 'id="verseTooltip"' in html:
        return html, False

    # CSS → just before </head>
    head_close = html.rfind('</head>')
    if head_close == -1:
        raise ValueError("No </head> tag found")
    html = html[:head_close] + TOOLTIP_CSS + '\n' + html[head_close:]

    # Div + JS → just before </body>
    body_close = html.rfind('</body>')
    if body_close == -1:
        raise ValueError("No </body> tag found")
    html = html[:body_close] + TOOLTIP_BLOCK + '\n' + html[body_close:]

    return html, True


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)

    infile, outfile = sys.argv[1], sys.argv[2]

    with open(infile, encoding='utf-8') as f:
        html = f.read()

    result, changed = inject(html)

    if not changed:
        print(f"Skipped — tooltip already present in {infile}")
        return

    with open(outfile, 'w', encoding='utf-8') as f:
        f.write(result)

    print(f"Done: tooltip injected → {outfile}")


if __name__ == '__main__':
    main()
