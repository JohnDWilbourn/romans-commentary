#!/usr/bin/env python3
"""
20260912_003_build_illuminations_index.py

Reads all illuminations HTML files from the illuminations-repo folder,
extracts content entries, and appends them to the romans-commentary
search-index.json.

Run from: /home/johndavid/Projects/Websites/Romans_Website/romans-commentary-git/

Usage:
    python3 20260912_003_build_illuminations_index.py
"""

import json
import os
import re
from html.parser import HTMLParser

# ── CONFIG ────────────────────────────────────────────────────────────────────

ILLUMINATIONS_DIR = '/home/johndavid/Projects/Websites/illuminations-repo'
SEARCH_INDEX_PATH = 'search-index.json'
BASE_URL = 'https://illuminations.intelligencereport.info'

# Files to skip
SKIP_FILES = {'index.html', 'CNAME', 'README.md'}

# Metadata for each illumination file
ILLUMINATION_META = {
    'romans_1_16-17.html': {
        'title': 'Romans 1:16–17 — The Pivot: From Salvation Gospel to the Living Gospel of Doctrine',
        'series': 'Romans · Chapter 22–23',
    },
    'chapter_33.html': {
        'title': 'φθόνος and φόνος: Jealousy, Murder, and the Grammar of Evil',
        'series': 'Romans · Chapter 33',
    },
    'forty_things.html': {
        'title': 'Forty Things: The Spiritual Assets of the Church Age Believer',
        'series': 'Soteriology · Church Age',
    },
    'eternal_security.html': {
        'title': 'Eternal Security — Ten Approaches to the Absolute Assurance of Salvation',
        'series': 'Salvation Theology',
    },
    'know_reckon_yield.html': {
        'title': 'Know, Reckon, Yield — The Operational Sequence of the Spirit-Filled Life',
        'series': 'Romans · Chapter 6',
    },
    'isaiah53.html': {
        'title': 'Isaiah 53 — The Suffering Servant and the Two Deaths of Christ',
        'series': 'Isaiah · The Servant Songs',
    },
    'pistis_faith_disclosure_dispensation.html': {
        'title': 'Pistis: The Four-Fold Development of Faith as Theological Disclosure and Experiential Dispensation',
        'series': 'Soteriology · Doctrine of Faith',
    },
    'faith_text_ages_rhetoric_lexicon_canon.html': {
        'title': 'Faith, Text, and the Shape of the Ages: Rhetoric, Lexicon, Canon, and the Doctrine of Pistis',
        'series': 'Apologetics · Hermeneutics',
    },
    'confronting_halstead_romans_4.html': {
        'title': 'Confronting Halstead on Romans 4',
        'series': 'Apologetics · Romans',
    },
    'confronting_the_reconfiguration_thesis.html': {
        'title': 'Confronting the Reconfiguration Thesis',
        'series': 'Apologetics · Hermeneutics',
    },
    'Discourse_The-Chapter-They-Skip.html': {
        'title': 'The Chapter They Skip — Isaiah 53 and the Haftarah Exclusion',
        'series': 'Isaiah · The Haftarah Question',
    },
}

# ── HTML PARSER ───────────────────────────────────────────────────────────────

class IlluminationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.entries = []
        self.current_section = ''
        self.current_section_id = ''
        self.current_h2 = ''
        self.current_h2_id = ''
        self.current_h3 = ''
        self.current_h3_id = ''
        self._capture = False
        self._tag_stack = []
        self._skip = False
        self._skip_tags = {'style', 'script', 'head', 'nav', 'button'}
        self._current_tag = ''
        self._buffer = ''

    def handle_starttag(self, tag, attrs):
        attr_dict = dict(attrs)
        self._tag_stack.append(tag)

        if tag in self._skip_tags:
            self._skip = True

        if tag == 'h2':
            self._capture = True
            self._current_tag = 'h2'
            self._buffer = ''
            self.current_h2_id = attr_dict.get('id', '')
            self.current_h3 = ''
            self.current_h3_id = ''

        elif tag == 'h3':
            self._capture = True
            self._current_tag = 'h3'
            self._buffer = ''
            self.current_h3_id = attr_dict.get('id', '')

        elif tag == 'p':
            self._capture = True
            self._current_tag = 'p'
            self._buffer = ''

        elif tag == 'blockquote':
            self._capture = True
            self._current_tag = 'blockquote'
            self._buffer = ''

    def handle_endtag(self, tag):
        if tag in self._skip_tags:
            self._skip = False

        if self._tag_stack and self._tag_stack[-1] == tag:
            self._tag_stack.pop()

        if tag == self._current_tag and self._capture:
            text = re.sub(r'\s+', ' ', self._buffer).strip()
            if text and len(text) > 20:
                if tag == 'h2':
                    self.current_h2 = text
                    self.current_section = text
                    self.current_section_id = self.current_h2_id
                elif tag == 'h3':
                    self.current_h3 = text
                elif tag in ('p', 'blockquote') and not self._in_skip():
                    # Detect Hebrew/Greek
                    greek = bool(re.search(r'[\u0370-\u03FF\u1F00-\u1FFF]', text))
                    hebrew = bool(re.search(r'[\u0590-\u05FF]', text))
                    # Detect verse references
                    verses = re.findall(
                        r'\b(?:Romans|Isaiah|Genesis|Luke|John|Acts|Galatians|'
                        r'Hebrews|Zechariah|Matthew|Mark|Ezekiel|Corinthians|'
                        r'Ephesians|Philippians|Colossians|Timothy|Peter|'
                        r'Revelation|Deuteronomy|Leviticus|Psalms?|Proverbs|'
                        r'1\s+\w+|2\s+\w+)\s+\d+[:\d–\-]*',
                        text
                    )
                    self.entries.append({
                        'section': self.current_h2,
                        'section_id': self.current_h2_id,
                        'subsection': self.current_h3,
                        'subsection_id': self.current_h3_id,
                        'kind': 'quote' if tag == 'blockquote' else 'body',
                        'text': text,
                        'verses': list(set(verses)),
                        'greek': greek,
                        'hebrew': hebrew,
                    })
            self._capture = False
            self._buffer = ''
            self._current_tag = ''

    def handle_data(self, data):
        if self._skip:
            return
        if self._capture:
            self._buffer += data

    def _in_skip(self):
        return any(t in self._skip_tags for t in self._tag_stack)


# ── MAIN ──────────────────────────────────────────────────────────────────────

def build_illumination_entries(filepath, filename, meta, id_prefix):
    with open(filepath, 'r', encoding='utf-8') as f:
        html = f.read()

    parser = IlluminationParser()
    parser.feed(html)

    url = f"{BASE_URL}/{filename}"
    title = meta.get('title', filename)
    series = meta.get('series', 'Illumination')

    entries = []
    for i, e in enumerate(parser.entries):
        entry_id = f"{id_prefix}-{i+1}"
        anchor = e['subsection_id'] or e['section_id'] or ''
        entries.append({
            'id': entry_id,
            'vol': 'illumination',
            'vol_label': f"Illumination — {title}",
            'chapter': series,
            'chapter_id': '',
            'section': e['section'],
            'section_id': e['section_id'],
            'subsection': e['subsection'],
            'subsection_id': e['subsection_id'],
            'kind': e['kind'],
            'text': e['text'],
            'verses': e['verses'],
            'greek': e['greek'],
            'hebrew': e['hebrew'],
            'url': url,
            'anchor': anchor,
        })
    return entries


def main():
    # Load existing index (Romans entries only)
    with open(SEARCH_INDEX_PATH, 'r', encoding='utf-8') as f:
        existing = json.load(f)

    # Strip any old illumination entries
    romans_entries = [e for e in existing if e.get('vol') != 'illumination']
    print(f"Romans entries: {len(romans_entries)}")

    # Build illumination entries
    all_illumination_entries = []
    html_files = sorted([
        f for f in os.listdir(ILLUMINATIONS_DIR)
        if f.endswith('.html') and f not in SKIP_FILES
    ])

    for filename in html_files:
        filepath = os.path.join(ILLUMINATIONS_DIR, filename)
        meta = ILLUMINATION_META.get(filename, {'title': filename, 'series': 'Illumination'})
        id_prefix = 'ill-' + filename.replace('.html', '').replace('_', '-').replace('.', '-')[:20]
        entries = build_illumination_entries(filepath, filename, meta, id_prefix)
        print(f"  {filename}: {len(entries)} entries")
        all_illumination_entries.extend(entries)

    print(f"Illumination entries: {len(all_illumination_entries)}")

    # Combine and write
    combined = romans_entries + all_illumination_entries
    with open(SEARCH_INDEX_PATH, 'w', encoding='utf-8') as f:
        json.dump(combined, f, ensure_ascii=False, separators=(',', ':'))

    print(f"Done. Total entries: {len(combined)} written to {SEARCH_INDEX_PATH}")


if __name__ == '__main__':
    main()
