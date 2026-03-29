#!/usr/bin/env python3
"""
20260328_001_build_search_index.py

Regenerates search-index.json from published HTML files.
Run from the romans-commentary-git directory.

Usage:
    python3 20260328_001_build_search_index.py

Output:
    search-index.json (overwrites existing)
"""

import json
import re
import os
from html.parser import HTMLParser

# ── Configuration ─────────────────────────────────────────────────────────────

HTML_FILES = [
    {
        "file": "20260319_003_Romans_Road.html",
        "vol": "vol1",
        "vol_label": "Volume I — Romans 1",
    },
    {
        "file": "20260321_001_Romans_Road_2.html",
        "vol": "vol2",
        "vol_label": "Volume II — Romans 2–3",
    },
]

OUTPUT_FILE = "search-index.json"

# ── Unicode range detection ────────────────────────────────────────────────────

def has_greek(text):
    return any('\u0370' <= c <= '\u03FF' or '\u1F00' <= c <= '\u1FFF' for c in text)

def has_hebrew(text):
    return any('\u0590' <= c <= '\u05FF' for c in text)

# ── Verse reference extraction ─────────────────────────────────────────────────

VERSE_RE = re.compile(
    r'\b(?:Romans|Genesis|Exodus|Leviticus|Numbers|Deuteronomy|Joshua|Judges|Ruth|'
    r'1\s*Samuel|2\s*Samuel|1\s*Kings|2\s*Kings|1\s*Chronicles|2\s*Chronicles|'
    r'Ezra|Nehemiah|Esther|Job|Psalm|Psalms|Proverbs|Ecclesiastes|Song of Solomon|'
    r'Isaiah|Jeremiah|Lamentations|Ezekiel|Daniel|Hosea|Joel|Amos|Obadiah|Jonah|'
    r'Micah|Nahum|Habakkuk|Zephaniah|Haggai|Zechariah|Malachi|Matthew|Mark|Luke|'
    r'John|Acts|1\s*Corinthians|2\s*Corinthians|Galatians|Ephesians|Philippians|'
    r'Colossians|1\s*Thessalonians|2\s*Thessalonians|1\s*Timothy|2\s*Timothy|Titus|'
    r'Philemon|Hebrews|James|1\s*Peter|2\s*Peter|1\s*John|2\s*John|3\s*John|Jude|'
    r'Revelation)\s+\d+(?::\d+(?:[-–]\d+)?)?(?:,\s*\d+(?::\d+(?:[-–]\d+)?)?)*',
    re.IGNORECASE
)

def extract_verses(text):
    return list(dict.fromkeys(VERSE_RE.findall(text)))

# ── HTML parser ────────────────────────────────────────────────────────────────

class CommentaryParser(HTMLParser):
    def __init__(self, vol, vol_label):
        super().__init__()
        self.vol = vol
        self.vol_label = vol_label
        self.entries = []
        self.counter = 0

        # State
        self.in_body = False          # True once we pass <div class="content"> or <main>
        self.in_nav = False
        self.current_tag = None
        self.current_attrs = {}
        self.capture = False
        self.buffer = []

        # Chapter / section tracking
        self.current_chapter = ""
        self.current_chapter_id = ""
        self.current_section = ""
        self.current_section_id = ""

        # Heading state
        self.heading_tag = None
        self.heading_id = None
        self.heading_class = None

        # Nesting depth for tags we skip
        self.skip_depth = 0
        self.skip_tags = {"script", "style", "nav", "header", "footer"}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)

        # Track nav to suppress nav text
        if tag == "nav" or attrs.get("class") in ("nav", "sidebar", "toc"):
            self.in_nav = True
            self.skip_depth += 1
            return

        if self.skip_depth > 0:
            self.skip_depth += 1
            return

        if tag in self.skip_tags:
            self.skip_depth += 1
            return

        # Detect content area
        cls = attrs.get("class", "")
        if tag in ("main", "article") or attrs.get("id") == "main" or "content" in cls or "commentary" in cls:
            self.in_body = True

        if not self.in_body:
            return

        # Headings
        if tag in ("h1", "h2", "h3", "h4"):
            self.heading_tag = tag
            self.heading_id = attrs.get("id", "")
            self.heading_class = attrs.get("class", "")
            self.capture = True
            self.buffer = []
            self.current_tag = tag
            self.current_attrs = attrs
            return

        # Paragraphs and block elements
        if tag in ("p", "blockquote", "li", "td", "th"):
            self.capture = True
            self.buffer = []
            self.current_tag = tag
            self.current_attrs = attrs

    def handle_endtag(self, tag):
        if self.skip_depth > 0:
            self.skip_depth -= 1
            if self.skip_depth == 0:
                self.in_nav = False
            return

        if not self.in_body:
            return

        if tag in ("h1", "h2", "h3", "h4") and self.capture and self.heading_tag == tag:
            text = self._flush()
            if not text:
                return

            # Update chapter/section tracking
            if tag == "h1" and "chapter" in (self.heading_class or "") or \
               (self.heading_id and self.heading_id.startswith("chapter-")):
                self.current_chapter = text
                self.current_chapter_id = self.heading_id or self._slugify(text)
                self.current_section = ""
                self.current_section_id = ""
            else:
                self.current_section = text
                self.current_section_id = self.heading_id or self._slugify(text)

            # Emit heading as entry
            self._emit(text, "heading")
            self.heading_tag = None

        elif tag in ("p", "blockquote", "li", "td", "th") and self.capture and self.current_tag == tag:
            text = self._flush()
            if text:
                kind = "blockquote" if tag == "blockquote" else "body"
                self._emit(text, kind)

    def handle_data(self, data):
        if self.capture and self.skip_depth == 0:
            self.buffer.append(data)

    def handle_entityref(self, name):
        entities = {"amp": "&", "lt": "<", "gt": ">", "quot": '"',
                    "apos": "'", "nbsp": " ", "mdash": "—", "ndash": "–",
                    "ldquo": "\u201C", "rdquo": "\u201D",
                    "lsquo": "\u2018", "rsquo": "\u2019"}
        if self.capture:
            self.buffer.append(entities.get(name, ""))

    def handle_charref(self, name):
        if self.capture:
            try:
                if name.startswith("x"):
                    char = chr(int(name[1:], 16))
                else:
                    char = chr(int(name))
                self.buffer.append(char)
            except (ValueError, OverflowError):
                pass

    def _flush(self):
        text = "".join(self.buffer).strip()
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text)
        self.buffer = []
        self.capture = False
        self.current_tag = None
        return text

    def _emit(self, text, kind):
        if not text or len(text) < 3:
            return
        self.counter += 1
        entry = {
            "id": f"{self.vol}-{self.counter}",
            "vol": self.vol,
            "vol_label": self.vol_label,
            "chapter": self.current_chapter,
            "chapter_id": self.current_chapter_id,
            "section": self.current_section,
            "section_id": self.current_section_id,
            "kind": kind,
            "text": text,
            "verses": extract_verses(text),
            "greek": has_greek(text),
            "hebrew": has_hebrew(text),
        }
        self.entries.append(entry)

    @staticmethod
    def _slugify(text):
        slug = text.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[\s_]+', '-', slug)
        slug = slug.strip('-')
        return slug


# ── Main ──────────────────────────────────────────────────────────────────────

def build_index():
    all_entries = []

    for spec in HTML_FILES:
        fpath = spec["file"]
        if not os.path.exists(fpath):
            print(f"WARNING: {fpath} not found — skipping.")
            continue

        with open(fpath, "r", encoding="utf-8") as f:
            html = f.read()

        parser = CommentaryParser(vol=spec["vol"], vol_label=spec["vol_label"])
        parser.feed(html)
        all_entries.extend(parser.entries)
        print(f"  {fpath}: {len(parser.entries)} entries extracted")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)

    print(f"\nDone. {len(all_entries)} total entries written to {OUTPUT_FILE}")


if __name__ == "__main__":
    build_index()
