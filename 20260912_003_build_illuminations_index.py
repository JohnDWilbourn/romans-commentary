#!/usr/bin/env python3
"""
20260912_003_build_illuminations_index.py

Reads all illuminations HTML files, extracts content entries,
and appends them to the romans-commentary search-index.json.

Run from: /home/johndavid/Projects/Websites/Romans_Website/romans-commentary-git/

Usage:
    python3 20260912_003_build_illuminations_index.py
"""

import json, os, re
from bs4 import BeautifulSoup

# ── CONFIG ────────────────────────────────────────────────────────────────────

ILLUMINATIONS_DIR = '/home/johndavid/Projects/Websites/illuminations-repo'
SEARCH_INDEX_PATH = 'search-index.json'
BASE_URL          = 'https://illuminations.intelligencereport.info'
SKIP_FILES        = {'index.html', 'CNAME', 'README.md'}

ILLUMINATION_META = {
    'romans_1_16-17.html': {
        'title':  'Romans 1:16–17 — The Pivot: From Salvation Gospel to the Living Gospel of Doctrine',
        'series': 'Romans · Chapter 22–23',
    },
    'chapter_33.html': {
        'title':  'φθόνος and φόνος: Jealousy, Murder, and the Grammar of Evil',
        'series': 'Romans · Chapter 33',
    },
    'forty_things.html': {
        'title':  'Forty Things: The Spiritual Assets of the Church Age Believer',
        'series': 'Soteriology · Church Age',
    },
    'eternal_security.html': {
        'title':  'Eternal Security — Ten Approaches to the Absolute Assurance of Salvation',
        'series': 'Salvation Theology',
    },
    'know_reckon_yield.html': {
        'title':  'Know, Reckon, Yield — The Operational Sequence of the Spirit-Filled Life',
        'series': 'Romans · Chapter 6',
    },
    'isaiah53.html': {
        'title':  'Isaiah 53 — The Suffering Servant and the Two Deaths of Christ',
        'series': 'Isaiah · The Servant Songs',
    },
    'pistis_faith_disclosure_dispensation.html': {
        'title':  'Pistis: The Four-Fold Development of Faith as Theological Disclosure and Experiential Dispensation',
        'series': 'Soteriology · Doctrine of Faith',
    },
    'faith_text_ages_rhetoric_lexicon_canon.html': {
        'title':  'Faith, Text, and the Shape of the Ages: Rhetoric, Lexicon, Canon, and the Doctrine of Pistis',
        'series': 'Apologetics · Hermeneutics',
    },
    'confronting_halstead_romans_4.html': {
        'title':  'Confronting Halstead on Romans 4',
        'series': 'Apologetics · Romans',
    },
    'confronting_the_reconfiguration_thesis.html': {
        'title':  'Confronting the Reconfiguration Thesis',
        'series': 'Apologetics · Hermeneutics',
    },
    'Discourse_The-Chapter-They-Skip.html': {
        'title':  'The Chapter They Skip — Isaiah 53 and the Haftarah Exclusion',
        'series': 'Isaiah · The Haftarah Question',
    },
}

VERSE_RE = re.compile(
    r'\b(?:Romans|Isaiah|Genesis|Exodus|Leviticus|Deuteronomy|'
    r'Joshua|Judges|Ruth|Samuel|Kings|Chronicles|Ezra|Nehemiah|Esther|'
    r'Job|Psalm|Psalms|Proverbs|Ecclesiastes|Song|Isaiah|Jeremiah|'
    r'Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|Micah|'
    r'Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|'
    r'Matthew|Mark|Luke|John|Acts|Galatians|Ephesians|Philippians|'
    r'Colossians|Thessalonians|Timothy|Titus|Philemon|Hebrews|James|'
    r'Peter|Jude|Revelation|Corinthians|'
    r'1\s+\w+|2\s+\w+|3\s+\w+)'
    r'\s+\d+[:\d–\-]*'
)

GREEK_RE  = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]')
HEBREW_RE = re.compile(r'[\u0590-\u05FF]')


def extract_entries(filepath, filename, meta):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Remove non-content tags
    for tag in soup(['style', 'script', 'head', 'nav', 'button',
                     'header', '.action-bar', '.back-link', '.nav-footer',
                     '.masthead', '#site-bar', '.vol-nav']):
        tag.decompose()

    url    = f"{BASE_URL}/{filename}"
    title  = meta.get('title', filename)
    series = meta.get('series', 'Illumination')

    entries  = []
    current_section    = ''
    current_section_id = ''
    current_sub        = ''
    current_sub_id     = ''

    # Walk all elements in document order
    for el in soup.find_all(['h2', 'h3', 'p', 'blockquote',
                              'li', 'td', 'div']):

        tag_name = el.name

        # Section tracking
        if tag_name == 'h2':
            current_section    = el.get_text(' ', strip=True)
            current_section_id = el.get('id', '')
            current_sub        = ''
            current_sub_id     = ''
            continue

        if tag_name == 'h3':
            current_sub    = el.get_text(' ', strip=True)
            current_sub_id = el.get('id', '')
            continue

        # Only index divs that carry content classes
        if tag_name == 'div':
            classes = el.get('class', [])
            content_classes = {
                'blessing-text', 'blessing-title', 'intro',
                'callout', 'content', 'doc-text', 'body-text'
            }
            if not any(c in content_classes for c in classes):
                continue
            # Don't double-index — skip if this div contains p tags
            if el.find('p'):
                continue

        text = el.get_text(' ', strip=True)
        text = re.sub(r'\s+', ' ', text).strip()

        if len(text) < 25:
            continue

        # Determine kind
        if tag_name == 'blockquote':
            kind = 'quote'
        elif tag_name in ('li', 'td'):
            kind = 'body'
        elif el.get('class') and any(
            c in ['blessing-title'] for c in el.get('class', [])
        ):
            kind = 'heading'
        else:
            kind = 'body'

        anchor = current_sub_id or current_section_id or ''

        entries.append({
            'id':            f"ill-{filename[:20].replace('.html','').replace('_','-')}-{len(entries)+1}",
            'vol':           'illumination',
            'vol_label':     f"Illumination — {title}",
            'chapter':       series,
            'chapter_id':    '',
            'section':       current_section,
            'section_id':    current_section_id,
            'subsection':    current_sub,
            'subsection_id': current_sub_id,
            'kind':          kind,
            'text':          text,
            'verses':        list(set(VERSE_RE.findall(text))),
            'greek':         bool(GREEK_RE.search(text)),
            'hebrew':        bool(HEBREW_RE.search(text)),
            'url':           url,
            'anchor':        anchor,
        })

    return entries


def main():
    with open(SEARCH_INDEX_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    romans_entries = [e for e in existing if e.get('vol') != 'illumination']
    print(f"Romans entries: {len(romans_entries)}")

    all_ill = []
    html_files = sorted([
        f for f in os.listdir(ILLUMINATIONS_DIR)
        if f.endswith('.html') and f not in SKIP_FILES
    ])

    for filename in html_files:
        filepath = os.path.join(ILLUMINATIONS_DIR, filename)
        meta     = ILLUMINATION_META.get(filename, {
            'title': filename, 'series': 'Illumination'
        })
        entries = extract_entries(filepath, filename, meta)
        print(f"  {filename}: {len(entries)} entries")
        all_ill.extend(entries)

    print(f"Illumination entries total: {len(all_ill)}")

    combined = romans_entries + all_ill
    with open(SEARCH_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Done. {len(combined)} total entries written to {SEARCH_INDEX_PATH}")


if __name__ == '__main__':
    main()
