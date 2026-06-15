# NA28 Greek Compliance Report — `romans-commentary`

**Repository:** JohnDWilbourn/romans-commentary
**Standard checked against:** Nestle–Aland *Novum Testamentum Graece*, 28th edition (NA28)
**Date:** 2026-06-14
**Scope:** All Greek text in the 7 `Romans_Road*.html` commentary volumes and `greek-guide.html`.

---

## Method

1. Stripped HTML tags and extracted every contiguous Greek-script run from all 8 files.
   - **6,764** Greek runs total (≈1,093 unique single-word lexeme citations, ≈457 unique multi-word phrases).
2. Ran objective polytonic-orthography validators that require **no** external text to adjudicate:
   - breathing marks on non-initial vowels (impossible in Greek);
   - word-initial vowels lacking a breathing mark (required in Greek);
   - grave accents off the ultima; doubled breathings;
   - Latin/Cyrillic letters fused into Greek words (mixed-script).
3. Compared the running-text verse quotations word-for-word against the NA28 text of Romans (and the cited cross-references: Phil 3:10, Eph 4:17, Col 3:2, Luke 18:13/19, John 1:14, Rom 6:8).
4. Re-verified every flagged item against the **raw HTML source** to exclude extraction artifacts, and recorded exact Unicode codepoints.

All findings below were confirmed present in the source files.

---

## Summary

| # | Severity | Category | Issue | Count |
|---|----------|----------|-------|-------|
| A | High | Breathing mark | Impossible/incorrect breathing marks | 3 distinct |
| B | High | Spelling | Wrong word / extra / missing letters | 4 distinct |
| C | Medium | Accent | Missing or wrong accent vs NA28 | 3 classes (9+ instances) |
| D | High | Mixed-script | Latin letters fused into Greek words | 3 distinct |
| E | Medium | Orthography | Missing diaeresis vs NA28 spelling | 1 (×1) |
| F | Low/Medium | Missing breathing | Lexeme citations lacking initial breathing | class (8+ verified) |
| G | Note | Methodology | Vice-list recast from NA28 inflected forms | — |

---

## A. Breathing-mark errors (High severity — objectively impossible/incorrect Greek)

### A1 — `θεὀν` → `θεόν`  (Romans 1:21)
- **File:** `Romans_Road.html`
- **Context:** *“διότι γνόντες τὸν **θεὀν** οὺχ ὡς θεὸν ἐδόξασαν…”*
- **Problem:** The omicron is `ὀ` = U+1F40 GREEK SMALL LETTER OMICRON **WITH PSILI (smooth breathing)**. A breathing mark can only stand on a word-**initial** vowel; here it sits on a medial vowel. The intended character is `ό` (omicron with acute).
- **NA28:** `θεόν`.

### A2 — `οὺχ` → `οὐχ`  (Romans 1:21)
- **File:** `Romans_Road.html`
- **Context:** *“…τὸν θεὀν **οὺχ** ὡς θεὸν…”*
- **Problem:** Initial upsilon is `ὺ` = U+1F7A UPSILON **WITH VARIA (grave)** instead of `ὐ` (upsilon with smooth breathing). A word-initial vowel must carry a breathing mark, not a bare grave.
- **NA28:** `οὐχ`.

### A3 — `ῶ ἄνθρωπε` → `ὦ ἄνθρωπε`  (Romans 2:1) — multiple instances (section headers)
- **File:** `Romans_Road_2.html`
- **Context:** *“IV. **ῶ ἄνθρωπε** — The Vocative Address”*, *“II. **ῶ ἄνθρωπε** and Κρίνω…”*
- **Problem:** `ῶ` = U+1FF6 OMEGA WITH PERISPOMENI (circumflex) **without a breathing**. The interjection requires smooth breathing: `ὦ` (U+1F66).
- **NA28:** `ὦ ἄνθρωπε`.

---

## B. Spelling errors (High severity — wrong, extra, or missing letters)

### B1 — `αὐθτῶν` → `αὐτῶν`  (Romans 1:21)
- **File:** `Romans_Road.html`
- **Context:** *“…ἐν τοῖς διαλογισμοῖς **αὐθτῶν** καὶ ἐσκοτίσθη…”*
- **Problem:** Intrusive `θ` (αὐ-**θ**-τῶν). Should be `αὐτῶν`.

### B2 — `ἀἀόρατα` → `ἀόρατα`  (Romans 1:20)
- **File:** `Romans_Road.html`
- **Context:** table cell *“τὰ **ἀἀόρατα** (όρατα αὐτοῦ)”*
- **Problem:** Doubled initial `ἀ`. Should be `ἀόρατα`. (Note the parenthetical `όρατα` is also missing its breathing.)

### B3 — `Ἰρις` → `Ἔρις`  (Romans 1:29)
- **File:** `Romans_Road.html`
- **Context:** heading *“Romans 1:29c–30a — **Ἰρις**, Δόλος, Κακοήθεια…”* and *“**Ἰρις** (strife/dissension)”*, *“A. **Ἰρις** — Dissension”*
- **Problem:** `Ἰρις` is *Iris* (the rainbow / goddess). The vice in Rom 1:29 is `ἔρις` (“strife”). **The author’s own gloss says “strife/dissension,”** confirming the intended word. Should be `Ἔρις`.

### B4 — `Ἅβριστής` → `Ὑβριστής`  (Romans 1:30)
- **File:** `Romans_Road.html`
- **Context:** *“Θεοστυγής (God-haters) · **Ἅβριστής** (insolent)…”*, *“C. **Ἅβριστής**, Ἀλαζών…”*, table *“**Ἅβριστής** (hubristes)”*
- **Problem:** Wrong initial vowel **and** breathing: `Ἅβριστής` (Α + rough breathing) for `ὑβριστής`. **The author’s transliteration “hubristes” and gloss “insolent” confirm** the intended word. Should be `Ὑβριστής`.

---

## C. Accent errors (Medium severity — verified against NA28)

### C1 — `Ἑλληνι` → `Ἕλληνι`  (Romans 2:9–10) — **3 instances**
- **File:** `Romans_Road_2.html`
- **Context:** *“Ἰουδαίῳ Πρῶτον καὶ **Ἑλληνι**…”* (×3)
- **Problem:** `Ἑ` = capital epsilon with **dasia only** (rough breathing, no accent); missing the acute. Should be `Ἕ` (dasia **and** oxia). The correct form `Ἕλληνι` appears only **once** in the corpus — the error outnumbers the correct spelling 3:1.
- **NA28 (Rom 2:9, 2:10):** `Ἕλληνι`.

### C2 — `κακών` → `κακῶν`  (Romans 1:30) — **5 instances**
- **File:** `Romans_Road.html`
- **Context:** *“…Ἀλαζών, Ἐφευρετής **κακών**…”*, *“Ἐφευρεταί **κακών**”*, etc.
- **Problem:** Genitive-plural ending `-ων`, when accented on the ultima, **always takes a circumflex**. `κακών` (acute) is orthographically impossible here. The correct `κακῶν` appears **0** times in the corpus.
- **NA28 (Rom 1:30):** `ἐφευρετὰς κακῶν`.

### C3 — `αὐτων` → `αὐτῶν`  (Ephesians 4:17, quoted in commentary)
- **File:** `Romans_Road_2.html`
- **Context:** *“…(ματαιότης τοῦ νοὸς **αὐτων**).”*
- **Problem:** Genitive-plural pronoun missing its circumflex on the ultima. Should be `αὐτῶν`.

*(Minor, same class: `ὑπομονήν` in “καθ’ ὑπομονήν ἔργου ἀγαθοῦ” (Rom 2:7) should be grave `ὑπομονὴν` in running text per NA28, since an acute on the ultima becomes grave before a following word.)*

---

## D. Mixed-script (Latin ↔ Greek) contamination (High severity)

### D1 — `mοιχεύω` → `μοιχεύω`  (Romans 2:22)
- **File:** `Romans_Road_2.html`
- **Context:** *“…of a Priest Nation · **mοιχεύω**, βδελύσσομαι…”*
- **Problem:** Begins with a **Latin** `m` (U+006D) instead of Greek `μ`. Renders/searches as a non-word. (The same lemma is correctly written `μοιχεύω` elsewhere in the file.)

### D2 — `toiouτos` → `τοιοῦτος`
- **File:** `Romans_Road_2.html`
- **Context:** *“The correlative adjective **toiouτos** (similar things)…”*
- **Problem:** Latin `toiou` fused to Greek `τος`. Should be the fully-Greek `τοιοῦτος`.

### D3 — `sὺn` → `σύν` / `syn`  (Romans 6:8 transliteration)
- **File:** `Romans_Road_6.html`
- **Context:** transliteration string *“pisteuomen hoti kai szēsomen **sὺn** autō”*
- **Problem:** Inside an otherwise-Latin transliteration, `sὺn` contains a stray Greek `ὺ`. Either the whole token should be Latin `syn` or the surrounding string should be Greek `σὺν αὐτῷ`. (Also note the transliteration `szēsomen` is missing a `u`: should be `syzēsomen` for `συζήσομεν`.)

---

## E. Diaeresis / spelling vs NA28 (Medium severity)

### E1 — `Μωυσέως` → `Μωϋσέως`  (Romans 5:14)
- **File:** `Romans_Road_5.html`
- **Context:** *“ἀπὸ ΑΔΑΜ μέχρι **Μωυσέως**.”*
- **Problem:** NA28 consistently prints the name with a **diaeresis** on the upsilon (`Μωϋσῆς`, gen. `Μωϋσέως`) to mark the separate vowel. The commentary omits it (`Μωυσέως`, plain upsilon).
- **NA28:** `Μωϋσέως`.

---

## F. Lexeme citations missing the initial breathing mark (Low–Medium)

A recurring pattern: Greek lemmas cited inline lose their required word-initial breathing. Verified examples with context:

| As written | Should be | Reference / context | File |
|------------|-----------|---------------------|------|
| `ειρήνην` | `εἰρήνην` | Rom 5:1 “ειρήνην ἔχομεν” | `Romans_Road_5.html` |
| `ανάστασις` | `ἀνάστασις` | lemma citation | `Romans_Road_5.html` |
| `επαγγελία` | `ἐπαγγελία` | lemma citation | `Romans_Road_4.html` |
| `επιμένω` | `ἐπιμένω` | “the present subjunctive of επιμένω” | `Romans_Road_6.html` |
| `υπομονή` | `ὑπομονή` | Rom 5:3–4 “endurance (υπομονή)” | `Romans_Road_5.html` |
| `αλλά` | `ἀλλά` | lemma list | `Romans_Road_2.html` |
| `εκ` | `ἐκ` | lemma citation | `Romans_Road*.html` |
| `οιχεύω` | `μοιχεύω` | see D1 (also missing μ) | `Romans_Road_2.html` |

This class should be swept programmatically (any Greek token beginning with a vowel and lacking U+0313/U+0314 in its initial vowel cluster is suspect). NB: alphabet-table cells in `greek-guide.html` (`Αα, Εε, Ηη …`) and all-caps display forms (`ΑΔΑΜ`) legitimately omit breathings and are **not** errors.

---

## G. Methodological note (not strictly an orthography error)

The vice catalog of Rom 1:29–31 is presented in **lemma / abstract-noun form** rather than NA28’s inflected text:
- NA28: `…ἐφευρετὰς κακῶν…`, `…ἀσυνέτους ἀσυνθέτους ἀστόργους ἀνελεήμονας` (accusative plural adjectives).
- Commentary: `Ἐφευρετής/Ἐφευρεταί`, `Ἀσύνετος, Ἀσύνθετος, Ἀστοργία, Ἀνελεήμων` (nominative singular / abstract nouns).

This is a legitimate pedagogical choice, but readers should not take these as verbatim NA28 wording. Where the **diacritics themselves** are wrong (C2 `κακών`, B3 `Ἰρις`, B4 `Ἅβριστής`), those remain genuine errors regardless of citation form.

---

## Recommended fixes (quick list)

```
Romans_Road.html      θεὀν     → θεόν        (Rom 1:21)
Romans_Road.html      οὺχ      → οὐχ         (Rom 1:21)
Romans_Road.html      αὐθτῶν   → αὐτῶν       (Rom 1:21)
Romans_Road.html      ἀἀόρατα  → ἀόρατα      (Rom 1:20)
Romans_Road.html      Ἰρις     → Ἔρις        (Rom 1:29, all occurrences)
Romans_Road.html      Ἅβριστής → Ὑβριστής    (Rom 1:30, all occurrences)
Romans_Road.html      κακών    → κακῶν       (Rom 1:30, ×5)
Romans_Road_2.html    ῶ ἄνθρωπε→ ὦ ἄνθρωπε   (Rom 2:1, headers)
Romans_Road_2.html    Ἑλληνι   → Ἕλληνι      (Rom 2:9–10, ×3)
Romans_Road_2.html    αὐτων    → αὐτῶν       (Eph 4:17 quote)
Romans_Road_2.html    mοιχεύω  → μοιχεύω     (Rom 2:22)
Romans_Road_2.html    toiouτos → τοιοῦτος
Romans_Road_5.html    Μωυσέως  → Μωϋσέως     (Rom 5:14)
Romans_Road_6.html    sὺn      → σύν / syn   (Rom 6:8 translit; also szēsomen→syzēsomen)
+ sweep all vowel-initial lemmas for missing breathing marks (Section F)
```

---

*Note on the search index:* `search-index.json` is generated from these HTML files, so it reproduces the same errors; regenerate it (`20260328_001_build_search_index.py`) after the source is corrected.
