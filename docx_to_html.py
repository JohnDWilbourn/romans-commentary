#!/usr/bin/env python3
"""
20260520_001_docx_to_html_patch.py
===================================
Patches docx_to_html.py to fix two issues found in Romans 6 docx files:

1. Duplicate glossary paragraph: a Normal paragraph immediately following
   the last table in a chapter contains the last glossary definition copied
   verbatim outside the table. This script strips it.

2. Normal paragraphs treated as body text: 1,859 body paragraphs are styled
   'Normal' instead of 'BodyText'. The converter was already handling Normal
   as body text but only in the final else branch. This patch makes it explicit.

Apply this patch by replacing the relevant section in docx_to_html.py.
The patched function is convert() — specifically the second-pass rendering loop.

HOW TO USE:
    This is a drop-in replacement for docx_to_html.py.
    Copy it to the Romans commentary repo and rename it docx_to_html.py,
    or use it directly:
    python3 20260520_001_docx_to_html_patch.py <input.docx> <output.html>
"""

import sys
import re
import zipfile
import html as htmlmod
from pathlib import Path
from xml.etree import ElementTree as ET

W  = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
WN = f'{{{W}}}'

SUBTITLE_PATTERN = re.compile(
    r'^(?:Romans|Galatians|Ephesians|Philippians|Colossians|'
    r'(?:First |Second |Third |1|2|3\s*)(?:Corinthians|Thessalonians|Timothy|Peter|John)|'
    r'Hebrews|James|Jude|Revelation|Genesis|Exodus|Psalms?|Proverbs?|Isaiah|Jeremiah|Ezekiel|Daniel)'
    r'\s+\d+[:\d–\-\.]+',
    re.IGNORECASE
)

CHAPTER_TITLE_PATTERN = re.compile(
    r'^Chapter\s+[A-Z][a-z]',
    re.IGNORECASE
)

GLOSSARY_HEADING_STYLES = {'GlossaryTableHeading'}
GLOSSARY_CELL_STYLES    = {'GlossaryTermColumn1','GreekGlossaryTerm',
                            'GreekGlossaryTransliteration','GlossaryDefinitionText'}
GLOSSARY_TABLE_STYLES   = GLOSSARY_HEADING_STYLES | GLOSSARY_CELL_STYLES

DATA_HEADING_STYLES     = {'TableHeading'}
DATA_CELL_STYLES        = {'TableContents'}
DATA_TABLE_STYLES       = DATA_HEADING_STYLES | DATA_CELL_STYLES

def _get_style(para):
    pPr = para.find(f'{WN}pPr')
    if pPr is None: return ''
    ps = pPr.find(f'{WN}pStyle')
    return ps.get(f'{WN}val', '') if ps is not None else ''

def _text(elem):
    parts = []
    for t in elem.iter(f'{WN}t'):
        parts.append(t.text or '')
    return ''.join(parts)

def _rich_text(para):
    parts = []
    for run in para.findall(f'{WN}r'):
        rpr  = run.find(f'{WN}rPr')
        text = ''.join(t.text or '' for t in run.findall(f'{WN}t'))
        if not text:
            continue
        text = htmlmod.escape(text)
        bold   = rpr is not None and rpr.find(f'{WN}b')   is not None
        italic = rpr is not None and rpr.find(f'{WN}i')   is not None
        if bold and italic:
            text = f'<strong><em>{text}</em></strong>'
        elif bold:
            text = f'<strong>{text}</strong>'
        elif italic:
            text = f'<em>{text}</em>'
        parts.append(text)
    return ''.join(parts)

def slugify(text):
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:80].strip('-')

def is_glossary_table(table):
    for row in table.findall(f'{WN}tr')[:2]:
        for cell in row.findall(f'{WN}tc'):
            for para in cell.findall(f'{WN}p'):
                s = _get_style(para)
                if s in GLOSSARY_TABLE_STYLES:
                    return True
                t = _text(para).strip().lower()
                if t == 'term':
                    return True
    return False

def is_data_table(table):
    for row in table.findall(f'{WN}tr')[:2]:
        for cell in row.findall(f'{WN}tc'):
            for para in cell.findall(f'{WN}p'):
                s = _get_style(para)
                if s in DATA_TABLE_STYLES:
                    return True
    return False

def get_last_glossary_cell_text(table):
    """Extract the text of the last cell in the last row of a glossary table.
    This is used to detect and strip the duplicate paragraph that follows."""
    rows = table.findall(f'{WN}tr')
    if not rows:
        return ''
    last_row = rows[-1]
    cells = last_row.findall(f'{WN}tc')
    if not cells:
        return ''
    last_cell = cells[-1]
    parts = []
    for para in last_cell.findall(f'{WN}p'):
        t = _text(para).strip()
        if t:
            parts.append(t)
    return ' '.join(parts)

def render_glossary_table(table, glossary_index):
    rows = table.findall(f'{WN}tr')
    lines = [
        f'<div class="glossary-wrap" id="glossary-{glossary_index}">',
        '  <p class="glossary-label">Glossary</p>',
        '  <table class="glossary-table"><tbody>',
    ]
    for row_idx, row in enumerate(rows):
        cells = row.findall(f'{WN}tc')
        is_header = row_idx == 0
        row_class = 'header-row' if is_header else ('' if row_idx % 2 == 0 else 'alt-row')
        lines.append(f'    <tr class="{row_class}">')
        for col_idx, cell in enumerate(cells):
            paras = cell.findall(f'{WN}p')
            cell_class = 'greek-cell' if col_idx == 1 else ''
            lines.append(f'      <td class="{cell_class}">')
            cell_parts = []
            for para in paras:
                t = _text(para).strip()
                if t:
                    cell_parts.append(htmlmod.escape(t))
            lines.append('\n'.join(cell_parts))
            lines.append('      </td>')
        lines.append('    </tr>')
    lines += ['  </tbody></table>', '</div>']
    return '\n'.join(lines)

def render_data_table(table):
    rows = table.findall(f'{WN}tr')
    lines = [
        '<div class="data-table-wrap">',
        '  <table class="data-table"><tbody>',
    ]
    for row_idx, row in enumerate(rows):
        cells = row.findall(f'{WN}tc')
        is_header = row_idx == 0
        first_styles = set()
        for cell in cells:
            for para in cell.findall(f'{WN}p'):
                s = _get_style(para)
                if s: first_styles.add(s)
        if first_styles & DATA_HEADING_STYLES:
            is_header = True
        row_class = 'header-row' if is_header else ('' if row_idx % 2 == 0 else 'alt-row')
        tag = 'th' if is_header else 'td'
        lines.append(f'    <tr class="{row_class}">')
        for cell in cells:
            paras = cell.findall(f'{WN}p')
            cell_parts = []
            for para in paras:
                t = _text(para).strip()
                if t:
                    cell_parts.append(htmlmod.escape(t))
            lines.append(f'      <{tag}>{" ".join(cell_parts)}</{tag}>')
        lines.append('    </tr>')
    lines += ['  </tbody></table>', '</div>']
    return '\n'.join(lines)

def build_nav(chapters):
    lines = ['<ul id="nav-list">']
    for chap_id, chap_title, sections in chapters:
        lines.append(f'  <li class="nav-h1"><a href="#{chap_id}">{htmlmod.escape(chap_title)}</a></li>')
        for sec_id, sec_title in sections:
            lines.append(f'  <li class="nav-h2"><a href="#{sec_id}">{htmlmod.escape(sec_title)}</a></li>')
    lines.append('</ul>')
    return '\n'.join(lines)

def convert(input_path: str, output_path: str):
    input_path  = Path(input_path)
    output_path = Path(output_path)

    with zipfile.ZipFile(input_path, 'r') as z:
        doc_xml = z.read('word/document.xml').decode('utf-8')

    root = ET.fromstring(doc_xml)
    body = root.find(f'{WN}body')

    # First pass: collect nav structure
    nav_chapters = []
    current_chapter = None
    current_sections = []
    chapter_count = 0

    for elem in body:
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'p':
            style = _get_style(elem)
            text  = _text(elem).strip()
            if not text:
                continue
            is_chapter_title = (style == 'Heading1' or
                (style in ('Normal', '') and re.match(r'^Chapter\s+[A-Z][a-z]', text, re.IGNORECASE)))
            if is_chapter_title:
                if current_chapter:
                    nav_chapters.append((current_chapter[0], current_chapter[1], current_sections))
                chapter_count += 1
                chap_id = f'chapter-{chapter_count}'
                current_chapter  = (chap_id, text)
                current_sections = []
            elif style == 'Heading2' and current_chapter:
                sec_id = slugify(text)
                current_sections.append((sec_id, text))

    if current_chapter:
        nav_chapters.append((current_chapter[0], current_chapter[1], current_sections))

    # -----------------------------------------------------------------------
    # PRE-PROCESS: identify duplicate glossary paragraphs to skip
    # A Normal paragraph immediately after the last glossary table in a chapter
    # contains the last glossary definition copied verbatim. We collect their
    # text fingerprints so we can skip them during rendering.
    # -----------------------------------------------------------------------
    elems = list(body)
    duplicate_skip_indices = set()

    last_glossary_table = None
    last_glossary_table_idx = None

    for idx, elem in enumerate(elems):
        tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if tag == 'tbl' and is_glossary_table(elem):
            last_glossary_table = elem
            last_glossary_table_idx = idx

    if last_glossary_table is not None:
        # Check the paragraph(s) immediately after the last glossary table
        last_cell_text = get_last_glossary_cell_text(last_glossary_table)
        if last_cell_text:
            # Look at the next 3 elements after the table for matching Normal paragraphs
            for idx in range(last_glossary_table_idx + 1,
                             min(last_glossary_table_idx + 4, len(elems))):
                elem = elems[idx]
                tag = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
                if tag == 'p':
                    style = _get_style(elem)
                    text  = _text(elem).strip()
                    # Match on first 60 chars to handle minor whitespace differences
                    if (style in ('Normal', '') and text and
                            last_cell_text[:60].lower() in text[:80].lower()):
                        duplicate_skip_indices.add(idx)

    # Second pass: render content
    content_lines = []
    chapter_count  = 0
    glossary_count = 0
    used_ids = {}

    def unique_id(base):
        count = used_ids.get(base, 0) + 1
        used_ids[base] = count
        return base if count == 1 else f'{base}-{count}'

    i = 0
    last_was_heading1 = False
    while i < len(elems):
        # Skip identified duplicate glossary paragraphs
        if i in duplicate_skip_indices:
            i += 1
            continue

        elem = elems[i]
        tag  = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag

        if tag == 'tbl':
            if is_glossary_table(elem):
                glossary_count += 1
                content_lines.append(render_glossary_table(elem, glossary_count))
            elif is_data_table(elem):
                content_lines.append(render_data_table(elem))
            else:
                content_lines.append(render_data_table(elem))
            i += 1
            continue

        if tag != 'p':
            i += 1
            continue

        style = _get_style(elem)
        text  = _text(elem).strip()
        rich  = _rich_text(elem)

        if style != 'Heading1' and not (last_was_heading1 and
                style in ('Normal', '', 'Header1Sub1')):
            last_was_heading1 = False

        if not text:
            content_lines.append('<div class="spacer"></div>')
            i += 1
            continue

        if style in ('Heading1', 'ListParagraph') and text:
            chapter_count += 1
            chap_id = f'chapter-{chapter_count}'
            content_lines.append(
                f'<h1 id="{chap_id}" class="chapter-title">{htmlmod.escape(text)}</h1>'
            )
            last_was_heading1 = True

        elif style == 'Header1Sub1':
            content_lines.append(
                f'<h2 class="chapter-subtitle">{htmlmod.escape(text)}</h2>'
            )
            last_was_heading1 = False

        elif style == 'Comment':
            content_lines.append(
                f'<p class="comment"><em>{htmlmod.escape(text)}</em></p>'
            )

        elif style == 'BlockQuotation':
            content_lines.append(
                f'<blockquote class="esv-quote">{rich}</blockquote>'
            )

        elif style == 'Heading2':
            sec_id = unique_id(slugify(text))
            content_lines.append(
                f'<h2 id="{sec_id}"><strong>{htmlmod.escape(text)}</strong></h2>'
            )

        elif style == 'Heading3':
            sec_id = unique_id(slugify(text))
            content_lines.append(
                f'<h3 id="{sec_id}"><strong>{htmlmod.escape(text)}</strong></h3>'
            )

        elif style == 'Conclusions':
            sec_id = unique_id(slugify(text))
            content_lines.append(
                f'<h2 id="{sec_id}" class="conclusions-heading"><strong>{htmlmod.escape(text)}</strong></h2>'
            )

        elif style in ('ConclusionsfromChapter', 'Conclusions from Chapter'):
            content_lines.append(
                f'<p class="conclusions-point">{rich}</p>'
            )

        elif style == 'Glossary':
            content_lines.append(
                f'<h2 id="glossary" class="glossary-section-heading"><strong>{htmlmod.escape(text)}</strong></h2>'
            )

        elif style in ('BodyText', 'Normal', ''):
            # FIX: Normal paragraphs that are chapter titles get treated as Heading1
            if text and CHAPTER_TITLE_PATTERN.match(text) and not re.search(r'has carried|[a-z]{3,}\s+[a-z]{3,}\s+[a-z]{3,}', text):
                chapter_count += 1
                chap_id = f'chapter-{chapter_count}'
                content_lines.append(
                    f'<h1 id="{chap_id}" class="chapter-title">{htmlmod.escape(text)}</h1>'
                )
                last_was_heading1 = True
            # FIX: Normal paragraphs are body text — treat identically to BodyText
            elif text:
                if last_was_heading1 and SUBTITLE_PATTERN.match(text):
                    content_lines.append(
                        f'<h2 class="chapter-subtitle">{htmlmod.escape(text)}</h2>'
                    )
                else:
                    content_lines.append(f'<p>{rich}</p>')

        else:
            if text:
                content_lines.append(f'<p>{rich}</p>')

        i += 1

    nav_html = build_nav(nav_chapters)

    page = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Romans Road — Volume VI</title>
  <link rel="stylesheet" href="style.css">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=EB+Garamond:ital,wght@0,400;0,600;1,400&display=swap" rel="stylesheet">
</head>
<body>

<div id="progress-bar"></div>

<button id="menu-toggle" aria-label="Open navigation">
  <span></span><span></span><span></span>
</button>

<div id="sidebar-overlay"></div>

<nav id="sidebar">
  <div id="sidebar-header">
    <h2>Romans Road</h2>
    <p>Volume VI — Romans 6</p>
  </div>
  <div id="vol-nav">
    <a href="Romans_Road.html">I</a>
    <a href="Romans_Road_2.html">II</a>
    <a href="Romans_Road_3.html">III</a>
    <a href="Romans_Road_4.html">IV</a>
    <a href="Romans_Road_5.html">V</a>
    <a href="Romans_Road_6.html" class="active">VI</a>
  </div>
  <input id="nav-search" type="text" placeholder="Search chapters…" aria-label="Search navigation">
  {nav_html}
</nav>

<main id="main">

{''.join(chr(10) + line for line in content_lines)}

</main>

<a href="#" id="top-btn">↑ Top</a>

<script src="nav.js"></script>
</body>
</html>'''

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(page, encoding='utf-8')
    print(f"Done — {output_path}")
    print(f"  Chapters:   {chapter_count}")
    print(f"  Glossaries: {glossary_count}")
    print(f"  Duplicate paragraphs stripped: {len(duplicate_skip_indices)}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Usage: python3 20260520_001_docx_to_html_patch.py <input.docx> <output.html>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
