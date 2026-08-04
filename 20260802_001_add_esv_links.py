#!/usr/bin/env python3
"""
20260802_001_add_esv_links.py
Add ESV.org verse links to Romans Road Commentary HTML volumes.

Requires: pip install beautifulsoup4 --break-system-packages

Usage:
    # Dry run — print all matches, write nothing:
    python3 20260802_001_add_esv_links.py Romans_Road.html --dry-run

    # Process a volume:
    python3 20260802_001_add_esv_links.py Romans_Road.html Romans_Road_linked.html

Handles:
    Full prose refs          Romans 1:3 / Job 19:23–27 / Genesis 18
    Paren semicolon cont.    (Acts 5:15; 16:18)     → Acts 5:15 and Acts 16:18
    Paren comma cont.        (1 Corinthians 4:6, 9) → 1 Cor 4:6 and 1 Cor 4:9

Skips text inside: <a>, <nav>, <script>, <style>, <head>, <noscript>, <code>, <pre>

NOTE: The ESV hover-tooltip script from the doctrine pages must be added to
each volume's <head> separately. The links produced here use class="esv-ref"
and href pointing to esv.org — the tooltip JS picks those up via [href*="esv.org"].
"""

import re
import sys
from bs4 import BeautifulSoup, NavigableString

# ── Book registry ─────────────────────────────────────────────────────────────
# Full names only (commentary uses no abbreviations).
# Longer entries must come first so the regex alternation matches greedily.
BOOKS = [
    "Song of Solomon", "Song of Songs",
    "1 Chronicles", "2 Chronicles",
    "1 Corinthians", "2 Corinthians",
    "1 Thessalonians", "2 Thessalonians",
    "1 Timothy", "2 Timothy",
    "1 Samuel", "2 Samuel",
    "1 Kings", "2 Kings",
    "1 Peter", "2 Peter",
    "1 John", "2 John", "3 John",
    "Genesis", "Exodus", "Leviticus", "Numbers", "Deuteronomy",
    "Joshua", "Judges", "Ruth", "Ezra", "Nehemiah", "Esther",
    "Job", "Psalms", "Psalm", "Proverbs", "Ecclesiastes",
    "Isaiah", "Jeremiah", "Lamentations", "Ezekiel", "Daniel",
    "Hosea", "Joel", "Amos", "Obadiah", "Jonah", "Micah",
    "Nahum", "Habakkuk", "Zephaniah", "Haggai", "Zechariah", "Malachi",
    "Matthew", "Mark", "Luke", "John", "Acts", "Romans",
    "Galatians", "Ephesians", "Philippians", "Colossians",
    "Titus", "Philemon", "Hebrews", "James", "Jude", "Revelation",
]

# Build alternation: longest names first to avoid prefix conflicts
_BOOKS_PAT = '|'.join(re.escape(b) for b in sorted(set(BOOKS), key=len, reverse=True))

# ── Core reference regex ──────────────────────────────────────────────────────
# Matches: BookName  chapter [ :verse [ –endverse ] ]
# Groups:  (1) book   (2) chapter   (3) verse?   (4) end_verse?
#
# (?<!\w) and (?!\w) prevent matching inside longer words.
# [ \u00a0]+ covers regular space and non-breaking space.
# [–\-] covers en dash (U+2013) and ASCII hyphen in ranges.
_VERSE_RE = re.compile(
    r'(?<!\w)'
    r'(' + _BOOKS_PAT + r')'
    r'[ \u00a0]+(\d+)'
    r'(?::(\d+)(?:[–\-](\d+))?)?'
    r'(?!\w)'
)

# Parenthetical group whose content starts with a book name.
# We only apply continuation logic inside parens.
_PAREN_RE = re.compile(r'\((' + _BOOKS_PAT + r'[^)]*)\)')

# Tags whose text content we leave untouched
_SKIP_TAGS = {'a', 'nav', 'script', 'style', 'head', 'title',
               'noscript', 'code', 'pre', 'svg'}


# ── Helpers ───────────────────────────────────────────────────────────────────
def _url(book, chapter, verse=None, end_verse=None):
    """Build an ESV.org URL for a verse reference."""
    b = book.replace(' ', '+')
    if b == 'Psalms':
        b = 'Psalm'          # ESV URLs use singular "Psalm"
    if verse is None:
        return f"https://www.esv.org/{b}+{chapter}/"
    if end_verse is None:
        return f"https://www.esv.org/{b}+{chapter}:{verse}/"
    return f"https://www.esv.org/{b}+{chapter}:{verse}-{end_verse}/"


def _in_skip_tag(node):
    """Return True if this text node lives inside a tag we should not touch."""
    p = node.parent
    while p:
        if getattr(p, 'name', None) in _SKIP_TAGS:
            return True
        p = p.parent
    return False


def _link(soup, display, url):
    """Build a BS4 <a> tag for an ESV link."""
    a = soup.new_tag('a', href=url, target='_blank')
    a['class'] = 'esv-ref'
    a.string = display
    return a


# ── Parenthetical content parser ──────────────────────────────────────────────
def _parse_paren_content(content):
    """
    Parse the text between the parens of a reference group, applying
    book/chapter inheritance for continuation patterns.

    Returns: list of (abs_start, abs_end, url, display_text) tuples,
             positions relative to `content`.

    Examples handled:
        "John 1:18; John 6:46; 1 Timothy 6:16"  →  three full refs, no continuation
        "Acts 5:15; 16:18"                       →  Acts 5:15 and Acts 16:18
        "1 Corinthians 4:6, 9"                   →  1 Cor 4:6 and 1 Cor 4:9
    """
    results = []
    cur_book = None
    cur_chapter = None
    pos = 0

    while pos < len(content):

        # ── Full reference (book + chapter + optional verse) ───────────────
        m = _VERSE_RE.match(content, pos)
        if m:
            cur_book = m.group(1)
            cur_chapter = m.group(2)
            results.append((
                m.start(), m.end(),
                _url(cur_book, cur_chapter, m.group(3), m.group(4)),
                m.group(0)
            ))
            pos = m.end()
            continue

        # ── Semicolon book-continuation:  "; chapter:verse" ───────────────
        # Same book as previous reference, new chapter and verse.
        if cur_book:
            m_semi = re.match(
                r'\s*;\s*(\d+):(\d+)(?:[–\-](\d+))?',
                content[pos:]
            )
            if m_semi:
                new_chapter = m_semi.group(1)
                verse       = m_semi.group(2)
                end_verse   = m_semi.group(3)
                prefix_len  = len(re.match(r'\s*;\s*', content[pos:]).group(0))
                abs_start   = pos + prefix_len
                abs_end     = pos + m_semi.end()
                results.append((
                    abs_start, abs_end,
                    _url(cur_book, new_chapter, verse, end_verse),
                    content[abs_start:abs_end]   # e.g. "16:18"
                ))
                cur_chapter = new_chapter
                pos = abs_end
                continue

        # ── Comma chapter-continuation:  ", verse" (same book AND chapter) ─
        # The (?!:) guard prevents matching "4" in something like ", 4:6".
        if cur_book and cur_chapter:
            m_comma = re.match(
                r'\s*,\s*(\d+)(?:[–\-](\d+))?(?!:)',
                content[pos:]
            )
            if m_comma:
                verse      = m_comma.group(1)
                end_verse  = m_comma.group(2)
                prefix_len = len(re.match(r'\s*,\s*', content[pos:]).group(0))
                abs_start  = pos + prefix_len
                abs_end    = pos + m_comma.end()
                results.append((
                    abs_start, abs_end,
                    _url(cur_book, cur_chapter, verse, end_verse),
                    content[abs_start:abs_end]   # e.g. "9"
                ))
                pos = abs_end
                continue

        pos += 1   # advance past any separator / text we can't use

    return results


# ── Segment builders ──────────────────────────────────────────────────────────
def _process_paren_groups(text):
    """
    First pass. Find parenthetical reference groups and process them with
    full continuation logic. Returns (segments, changed).

    `segments` is a list of:
        str             — plain text
        (display, url)  — a reference that should become a link
    """
    segments = []
    last_end = 0
    changed  = False

    for pm in _PAREN_RE.finditer(text):
        content = pm.group(1)
        refs    = _parse_paren_content(content)
        if not refs:
            continue

        # Text before this paren group
        if pm.start() > last_end:
            segments.append(text[last_end:pm.start()])

        segments.append('(')

        # Interleave plain text with link tuples within the group
        c_last = 0
        for (start, end, url, display) in refs:
            if start > c_last:
                segments.append(content[c_last:start])
            segments.append((display, url))
            c_last  = end
            changed = True
        if c_last < len(content):
            segments.append(content[c_last:])

        segments.append(')')
        last_end = pm.end()

    # Remaining text after the last paren group
    if last_end < len(text):
        segments.append(text[last_end:])

    return segments, changed


def _process_prose_refs(segments):
    """
    Second pass. For each plain-string segment, find any full references
    (book + chapter + optional verse) that were not already caught inside
    a parenthetical group, and convert them to link tuples.
    """
    result = []
    for seg in segments:
        if not isinstance(seg, str):
            result.append(seg)   # already a (display, url) tuple — leave it
            continue

        sub   = []
        c_end = 0
        found = False
        for m in _VERSE_RE.finditer(seg):
            if m.start() > c_end:
                sub.append(seg[c_end:m.start()])
            sub.append((
                m.group(0),
                _url(m.group(1), m.group(2), m.group(3), m.group(4))
            ))
            c_end = m.end()
            found = True

        if not found:
            result.append(seg)
        else:
            if c_end < len(seg):
                sub.append(seg[c_end:])
            result.extend(sub)

    return result


# ── DOM surgery ───────────────────────────────────────────────────────────────
def _replace_node(soup, node, segments):
    """
    Replace a NavigableString `node` with a sequence of text nodes and <a> tags
    built from `segments`. Uses a temporary <span> + unwrap() for clean insertion.
    """
    wrapper = soup.new_tag('span')
    for seg in segments:
        if isinstance(seg, str):
            wrapper.append(NavigableString(seg))
        else:
            display, url = seg
            wrapper.append(_link(soup, display, url))
    node.replace_with(wrapper)
    wrapper.unwrap()


# ── Entry point ───────────────────────────────────────────────────────────────
def process_html(html_str, dry_run=False):
    soup = BeautifulSoup(html_str, 'html.parser')

    # Collect qualifying text nodes before we touch the tree
    candidates = [
        n for n in soup.find_all(string=True)
        if not _in_skip_tag(n) and _VERSE_RE.search(str(n))
    ]

    total_links = 0

    for node in candidates:
        text = str(node)

        # Pass 1: parenthetical groups (with continuation logic)
        segments, _ = _process_paren_groups(text)

        # Pass 2: remaining full references in prose
        segments = _process_prose_refs(segments)

        link_count = sum(1 for s in segments if isinstance(s, tuple))
        if link_count == 0:
            continue

        total_links += link_count

        if dry_run:
            parent_tag = getattr(node.parent, 'name', '?')
            print(f"\n[<{parent_tag}>]  {text[:80].strip()!r}")
            for seg in segments:
                if isinstance(seg, tuple):
                    print(f"    {seg[0]!r:35s}  →  {seg[1]}")
        else:
            _replace_node(soup, node, segments)

    return str(soup), total_links


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    infile   = sys.argv[1]
    dry_run  = '--dry-run' in sys.argv
    outfile  = None if dry_run else (sys.argv[2] if len(sys.argv) > 2 else None)

    if not dry_run and outfile is None:
        print("Error: supply an output filename, or pass --dry-run")
        sys.exit(1)

    with open(infile, encoding='utf-8') as f:
        html = f.read()

    result, total = process_html(html, dry_run=dry_run)

    if dry_run:
        print(f"\n{'─'*60}")
        print(f"Total references found: {total}  (dry run — nothing written)")
    else:
        with open(outfile, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"Done: {total} ESV links added → {outfile}")


if __name__ == '__main__':
    main()
