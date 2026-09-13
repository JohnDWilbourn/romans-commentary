#!/usr/bin/env python3
"""
20260804_001_build_scripture_index_resources.py
Add Romans Road chapter references to scripture index Resources column.

Scans all 8 processed Romans Road HTML volumes, extracts cited verses,
classifies as Level 1 (chapter-subtitle verse — bold link) or Level 2
(body citation — plain link), then appends chapter links to the Resources
column of each matching row in the scripture index.

Usage:
    python3 20260804_001_build_scripture_index_resources.py

Idempotent: skips rows that already contain 'Romans Road'.
"""

import re
import sys
from pathlib import Path
from bs4 import BeautifulSoup

# ── Paths ─────────────────────────────────────────────────────────────────────
VOLUMES_DIR  = Path('/home/johndavid/Projects/Websites/Romans_Website/romans-commentary-git')
INDEX_PATH   = Path('/home/johndavid/Projects/Websites/study-hall/doctrines/scripture-index.html')
COMMENTARY   = 'https://commentary.intelligencereport.info'

VOLUMES = [
    ('Romans_Road.html',   'I'),
    ('Romans_Road_2.html', 'II'),
    ('Romans_Road_3.html', 'III'),
    ('Romans_Road_4.html', 'IV'),
    ('Romans_Road_5.html', 'V'),
    ('Romans_Road_6.html', 'VI'),
    ('Romans_Road_7.html', 'VII'),
    ('Romans_Road_8.html', 'VIII'),
]

# ── ESV URL parser ────────────────────────────────────────────────────────────
# Greedy book match so "1 Corinthians 4:6" → ("1 Corinthians", "4:6")
_REF_RE = re.compile(r'^(.+)\s+(\d+(?::\d+(?:-\d+)?)?)\s*$')

def parse_esv_url(href):
    """Return (book, ref) from an esv.org URL, or (None, None)."""
    if not href or 'esv.org' not in href:
        return None, None
    s = href.replace('https://www.esv.org/', '').rstrip('/')
    s = s.replace('+', ' ').replace('\u2013', '-').replace('\u2014', '-')
    m = _REF_RE.match(s)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, None

# ── Volume scanner ────────────────────────────────────────────────────────────
def scan_volume(filepath, vol_roman):
    """
    Return list of dicts:
        {book, ref, level (1|2), vol, chapter_num, url}
    """
    with open(filepath, encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    filename  = filepath.name
    base_url  = f'{COMMENTARY}/{filename}'
    entries   = []

    for h1 in soup.find_all('h1', class_='chapter-title'):
        chapter_id  = h1.get('id', '')
        if not chapter_id:
            continue
        chapter_num = chapter_id.replace('chapter-', '')
        chapter_url = f'{base_url}#{chapter_id}'

        # Collect all siblings until the next chapter heading
        siblings = []
        el = h1.find_next_sibling()
        while el:
            if el.name == 'h1' and 'chapter-title' in el.get('class', []):
                break
            siblings.append(el)
            el = el.find_next_sibling()

        seen_in_chapter = set()  # deduplicate within a chapter

        # ── Level 1: verse(s) in the chapter-subtitle h2 ─────────────────────
        subtitle_refs = set()
        for sib in siblings:
            if sib.name == 'h2' and 'chapter-subtitle' in sib.get('class', []):
                for a in sib.find_all('a', class_='esv-ref'):
                    book, ref = parse_esv_url(a.get('href', ''))
                    if book and ref:
                        key = (book, ref)
                        subtitle_refs.add(key)
                        if key not in seen_in_chapter:
                            seen_in_chapter.add(key)
                            entries.append({
                                'book': book, 'ref': ref, 'level': 1,
                                'vol': vol_roman, 'chapter_num': chapter_num,
                                'url': chapter_url
                            })
                break  # only the first h2.chapter-subtitle

        # ── Level 2: all other esv-ref links in the chapter body ──────────────
        for sib in siblings:
            # Skip subtitle and doc-actions
            if sib.name == 'h2' and 'chapter-subtitle' in sib.get('class', []):
                continue
            if sib.name == 'div' and 'doc-actions' in sib.get('class', []):
                continue
            for a in sib.find_all('a', class_='esv-ref'):
                book, ref = parse_esv_url(a.get('href', ''))
                if book and ref:
                    key = (book, ref)
                    if key not in seen_in_chapter:
                        seen_in_chapter.add(key)
                        entries.append({
                            'book': book, 'ref': ref, 'level': 2,
                            'vol': vol_roman, 'chapter_num': chapter_num,
                            'url': chapter_url
                        })

    return entries

# ── Link builder ──────────────────────────────────────────────────────────────
def make_link(r):
    text = f"Romans Road · Vol. {r['vol']}, Ch. {r['chapter_num']}"
    link = f'<a href="{r["url"]}" target="_blank">{text}</a>'
    return f'<strong>{link}</strong>' if r['level'] == 1 else link

# ── Index updater (string-based, preserves formatting) ────────────────────────
# Matches one table row: captures book, ESV href, excerpt td, resources content
_ROW_RE = re.compile(
    r'(<tr>\s*<td>([^<]+)</td>\s*<td><a href="([^"]+)" target="_blank">[^<]*</a></td>'
    r'\s*<td>.*?</td>\s*<td>)(.*?)(</td>\s*</tr>)',
    re.DOTALL
)

def update_index(index_path, verse_map):
    with open(index_path, encoding='utf-8') as f:
        html = f.read()

    count = [0]

    def row_repl(m):
        book            = m.group(2).strip()
        esv_href        = m.group(3)
        current_res     = m.group(4)

        if 'Romans Road' in current_res:
            return m.group(0)  # idempotent

        _, ref = parse_esv_url(esv_href)
        if not ref:
            return m.group(0)

        key = (book, ref)
        if key not in verse_map:
            return m.group(0)

        new_links   = ', '.join(make_link(r) for r in verse_map[key])
        new_res     = (current_res.rstrip() + ', ' + new_links
                       if current_res.strip() else new_links)
        count[0]   += 1
        return m.group(1) + new_res + m.group(5)

    new_html = _ROW_RE.sub(row_repl, html)

    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_html)

    return count[0]

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    all_entries = []
    for filename, vol_roman in VOLUMES:
        path = VOLUMES_DIR / filename
        if not path.exists():
            print(f'Missing: {path} — skipped')
            continue
        entries = scan_volume(path, vol_roman)
        print(f'Vol. {vol_roman:>4s}: {len(entries):4d} verse-chapter pairs scanned')
        all_entries.extend(entries)

    # Build verse → [entries] map
    verse_map = {}
    for e in all_entries:
        key = (e['book'], e['ref'])
        verse_map.setdefault(key, []).append(e)

    print(f'\nUnique verse references across all volumes: {len(verse_map)}')

    updated = update_index(INDEX_PATH, verse_map)
    print(f'Scripture index rows updated: {updated}')
    print(f'Output: {INDEX_PATH}')

if __name__ == '__main__':
    main()
