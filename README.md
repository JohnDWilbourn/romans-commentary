# Romans Road Commentary — Project README
## For Claude: Read This First

---

## Site

- **Live site:** https://commentary.intelligencereport.info
- **GitHub repo:** https://github.com/JohnDWilbourn/romans-commentary
- **Local repo:** `/home/johndavid/Projects/Websites/Romans_Website/romans-commentary-git/`

---

## Owner

John David — independent biblical scholar, author, intelligence analyst.
- Works outside denominational constraints
- Dispensational framework: R.B. Thieme Jr. and Lewis Sperry Chafer
- Explicitly rejects Reformed/Calvinist frameworks
- Greek study via biblical immersion, seven-year mastery goal
- Hardware: Celeron J4105 laptop (Ubuntu Linux), Samsung S25 Ultra, Samsung S24 FE
- Tight budget. Print books preferred over software for primary study.

---

## Rules — Never Violate These

1. **ALWAYS serial number every output file:** `YYYYMMDD_NNN_filename.ext`
   Example: `20260319_001_Romans_Road.html`, `20260319_002_docx_to_html.py`
   Never output a generic filename.

2. **Never ask clarifying questions using the ask_user_input widget.** Plain text only.

3. **Never rename John David's scripts without permission.**

4. **Never make multi-file changes without explicit instruction for each file.**

5. **One change at a time. Verify before next change.**

6. **Never touch HTML files for nav/CSS changes — use nav.js and style.css only.**

7. **Content is sacred. Code is expendable.**

---

## Pipeline

```
.mp3 → Whisper → .txt → process_transcripts.py (Claude API) → .py → build_chapter.py → .docx → docx_to_html.py → .html → GitHub Pages
```

### Key script locations
- `process_transcripts.py` — `/home/johndavid/Projects/My Book/Instructions/process_transcripts.py`
- `build_chapter.py` — `/home/johndavid/Projects/My Book/Instructions/build_chapter.py`
- `INSTRUCTIONS.md` — `/home/johndavid/Projects/My Book/Instructions/INSTRUCTIONS.md`
- `docx_to_html.py` — in repo root and `/home/johndavid/Projects/Websites/Files/`
- API key — `/home/johndavid/Projects/My Book/Instructions/API_Key.txt` or `export ANTHROPIC_API_KEY=...`

### Romans series folder structure
```
/home/johndavid/Projects/My Book/Romans4/
├── Romans4_txt/     ← transcript input (458_0108.txt–458_0127.txt)
├── Romans4_py/      ← API output (.py chapter scripts)
└── Romans4_docx/    ← built chapter .docx files
```

### Audio transcription
- Whisper tiny model — works on laptop
- Basics 1961 (101 series): 28 mp3s at `/home/johndavid/Projects/RB_Thieme/Streaming_files/Basics_1961/`
- Basics 1969 (102 series): 84 mp3s
- Output: `/home/johndavid/Projects/RB_Thieme/Transcripts/`
- 1 Corinthians mp3s: `/home/johndavid/Projects/My Book/1_Corinthians/408_mp3/`
- 1 Corinthians txt output: `/home/johndavid/Projects/My Book/1_Corinthians/408_txt/`

---

## Site Structure

```
romans-commentary-git/
├── index.html                  ← Site landing page
├── Romans_Road.html            ← Volume I (Romans 1, 35 chapters)
├── Romans_Road_2.html          ← Volume II (Romans 2, 18 chapters)
├── Romans_Road_3.html          ← Volume III (Romans 3, 34 chapters)
├── illuminations.html          ← Illuminations index
├── illuminations/
│   ├── romans_1_16-17.html
│   ├── chapter_33.html
│   └── forty_things.html
├── greek-guide.html            ← Greek grammar reference
├── search.html                 ← Search page (needs rebuild)
├── search-index.json           ← Search index (needs rebuild)
├── style.css                   ← Global stylesheet
├── nav.js                      ← All JavaScript including site nav
├── sw.js                       ← Service worker
├── manifest.json
└── CNAME
```

### Spiritual Growth Lessons
- Live at: `lessons.intelligencereport.info`
- Lessons 001–003 deployed
- Lesson 004 planned: "Confession" — Genesis 3, David's Psalms, 1 John 1:9
- **These are NOT in the nav yet — URL structure needed before adding**

---

## Navigation Architecture

### Sidebar (chapter nav)
- Lives inside each Romans volume HTML file
- Chapter-by-chapter navigation for the current volume only
- Controlled by `nav.js` → `initSectionObserver()`
- Do NOT put site-wide links here

### Site Top Nav
- Injected by `nav.js` → `initSiteNav()` into every page that loads nav.js
- Config lives in `SITE_NAV` array at top of nav.js
- **To add a new section: add one entry to SITE_NAV. Nothing else changes.**
- Current categories: Commentary, Illuminations, Language, Search, Home
- Lessons not yet added — need URL structure first

### CSS for site top nav
- Lives in `style.css` at the bottom
- ID: `#site-top-nav`
- Dropdowns: `.site-nav-dropdown` `.site-nav-menu`

---

## Docx Style Registry

Every chapter docx uses these styles (from Romans1.docx template):

| StyleId | HTML output |
|---------|-------------|
| Heading1 | `<h1 class="chapter-title" id="chapter-N">` |
| Header1Sub1 | `<h2 class="chapter-subtitle">` |
| Comment | `<p class="comment"><em>` |
| BlockQuotation | `<blockquote class="esv-quote">` |
| Heading2 | `<h2 id="...">` |
| Heading3 | `<h3 id="...">` |
| BodyText | `<p>` |
| Conclusions | `<h2 class="conclusions-heading" id="...">` |
| ConclusionsfromChapter | `<p class="conclusions-point">` |
| Glossary | `<h2 class="glossary-section-heading" id="glossary-chapter-N">` |
| GlossaryTableHeading | Header row of glossary table |
| GlossaryTermColumn1 | Col 0 of glossary table |
| GreekGlossaryTerm | Col 1 line 1 |
| GreekGlossaryTransliteration | Col 1 line 2 |
| GlossaryDefinitionText | Col 2 |
| TableHeading | `<th>` in data table |
| TableContents | `<td>` in data table |
| Normal | Falls back to `<p>` |

---

## Theological Framework

- **Central axis of Romans:** δικαιοσύνη θεοῦ = justice of God (not "righteousness")
- **Three adjustments:** salvation, rebound (1 John 1:9), maturity
- **Rebound:** naming known sins to God — not performance, not emotion
- **μετανοέω:** change of mind — NOT "repentance" in the performative sense
- **No Lucifer/Isaiah 14** — Angelic Conflict built on Ezekiel 28, Rev 12, John 8:44
- **LXX-first** for Paul's OT citations
- **NA28** as critical text, not Textus Receptus
- **Wallace** eight-case Greek grammar system throughout
- **No Thieme terminology on public site** — use standard theological equivalents
  - "drop zone" → "mediated grace" or "judicial grace"
  - "rebound" → "confession" or "restoration of fellowship"

---

## Curriculum: Spiritual Growth Lessons

Four-layer, six-phase HTML curriculum at `lessons.intelligencereport.info`:

1. **Identity:** Growth Beyond Salvation, Royal Priest, Royal Ambassador
2. **Integrity/PSDs:** Confession, Spirit-filling, Faith-Rest, Grace Orientation, Doctrinal Orientation, Sense of Destiny, Personal Love for God, Impersonal Love, Contentment, Occupation with Christ
3. **Suffering/testing**
4. **Rewards/Kingdom**

Planned lessons:
- 004: Confession (not "Rebound") — Genesis 3, David's Psalms, 1 John 1:9
- 005: Faith
- 006: Repentance
- Election (future)
- Bridge: Proverbs 10:25
- Kingdom Reality: Luke 17:21, Col 1:13
- Grace and Love (2-part): John 3 (Nicodemus), John 4 (Samaritan woman)
- Socratic front-door pre-Lesson 000

---

## What Needs Doing (Current State — April 3, 2026)

1. **Site nav** — top nav injected by nav.js is rendering as vertical list, not horizontal bar. CSS likely not applied correctly. Fix: verify `site-nav.css` contents are in `style.css`.

2. **Lessons not in nav** — need URL structure for lessons.intelligencereport.info pages before adding to SITE_NAV config.

3. **Search broken** — `search.html` layout is empty with misplaced input. `search-index.json` needs full rebuild from all three volumes. Both need to be rewritten from scratch.

4. **Romans 3 remaining chapters** — 17 chapters still to complete in the docx.

5. **Romans 4** — 20 transcripts ready (`458_0108.txt–458_0127.txt`), `process_transcripts.py` pipeline ready, API key must be set via `export ANTHROPIC_API_KEY=...`

6. **Romans 2 docx** — 83 of 318 pages hard-styled, remainder soft/mixed. Needs completion before HTML regeneration.

7. **Vol I and Vol II nav** — need Volume III link added (was done via sed but may have been lost in restore).

8. **index.html** — needs Volume III card and site-wide framing as content grows beyond Romans.

---

## Search Index Format

Each entry in `search-index.json`:
```json
{
  "title": "Section heading text",
  "chapter": "Chapter One",
  "chapter_id": "chapter-1",
  "section_id": "i-the-theme-of-romans",
  "url": "Romans_Road.html#i-the-theme-of-romans"
}
```

---

## Important History

- Site was broken by multi-file layout changes. Restored via git.
- Do not restructure layout across multiple files simultaneously.
- The sidebar `position:sticky` with `top:0` conflicts with a site bar — if adding top bar, adjust sidebar `top` and `height` in CSS only, not in HTML.
- `docx_to_html.py` generates clean HTML — 52/52 tables closed, all divs balanced for Vol I.
- Smart quotes in API-generated `.py` files cause SyntaxErrors — sanitize with: `.replace('\u201c', '\\"').replace('\u201d', '\\"')`

