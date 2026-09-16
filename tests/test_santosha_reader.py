# -*- coding: utf-8 -*-
"""#315 — the Santosha reader (events/santosha-pys-2-42-2026-09/reader), built from the corpus.
#316 adds a SUTRA level above the decks, so the reader can hold more than one sutra.

NAMED FAILURES:
  (a) A CARD WITHOUT SPANISH — the owner asked for English + Spanish on every card; the toggle
      would silently show English for it. Every shown card must carry a non-empty md_es.
  (b) THE STALE BUILD — santosha-reader.html must carry the ES toggle, the T key and every deck
      in decks.json; a rebuild from an old template would drop the language feature.
  (c) THE FIRST TAB — the Satyananda rendering of II.42 from Four Chapters on Freedom must be the
      FIRST card of the FIRST tab, and the Vyāsa + one contemporary rendering must follow it
      (owner's order for the talk).
  (d) THE ETYMOLOGY TAB — santoṣa must be on it, and the family table must reach the page as a
      real <table> (marked's gfm tables), not as pipe characters.
  (e) THE SILENT MIGRATION — #316 moves every deck under a "sutras" level; a migration that drops,
      reorders or mutates a single card's text while doing so is worse than one that crashes,
      because nothing on the page would say so.
  (f) THE STRIP NOBODY NOTICES — the sutra strip must render even with one sutra, or the room
      never learns the affordance before a second sutra ships; and switching sutras must not leak
      one sutra's favourites or reading position into another's.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# ajna keeps the reader under events/; the public export (scripts/export_sutra_reader.py) puts
# decks.json at the repo root and builds index.html. The same guards run in both trees.
_nested = REPO / "events" / "santosha-pys-2-42-2026-09" / "reader"
R = _nested if (_nested / "decks.json").is_file() else REPO
DECKS_JSON = json.loads((R / "decks.json").read_text(encoding="utf-8"))
SUTRAS = DECKS_JSON["sutras"]
DECKS = [d for s in SUTRAS for d in s["decks"]]
CONFIG = json.loads((R / "config.json").read_text(encoding="utf-8"))
HTML = (R / CONFIG.get("output", "santosha-reader.html")).read_text(encoding="utf-8")
SHOWN_KINDS = {k for t in CONFIG["tabs"] for k in t["kinds"]}


def test_every_shown_card_has_spanish():
    missing = [(d["id"], i["id"]) for d in DECKS if d["kind"] in SHOWN_KINDS
               for i in d["items"] if not (i.get("md_es") or "").strip() and 'lang="es"' not in i["md"]]  # inline bilingual cards carry both
    assert not missing, f"(a) cards without md_es: {missing}"


def test_the_build_carries_the_language_toggle_and_every_deck():
    assert 'id="langBtn"' in HTML and 'e.key === "l" || e.key === "L"' in HTML, "(b) the ES toggle is not in the build"
    for d in DECKS:
        assert d["id"] in HTML, f"(b) deck {d['id']} missing from the build"
    assert "<title>Sutra Reader</title>" in HTML


def test_the_sutra_tab_opens_with_satyananda_then_vyasa_then_a_contemporary():
    first_tab_kinds = CONFIG["tabs"][0]["kinds"]
    sutra = [d for d in DECKS if d["kind"] in first_tab_kinds]
    assert sutra and sutra[0]["items"][0]["book"] == "Four Chapters on Freedom", "(c)"
    who = [i["attributed"] for i in sutra[0]["items"]]
    assert who[0].startswith("Swami Satyananda") and "Vyāsa" in who[1] and who[2] == "Osho", who


def test_etymology_tab_has_santosha_and_a_real_table():
    ety = [d for d in DECKS if d["kind"] == "etymology"]
    titles = [i["title"] for d in ety for i in d["items"]]
    assert any(t.startswith("Santoṣa") for t in titles), "(d) santoṣa is not on the etymology tab"
    table_card = next(i for d in ety for i in d["items"] if i["id"] == "ety:all")
    assert table_card["md"].count("|") > 40 and "Sannyāsa" in table_card["md"], "(d) the family table is missing rows"
    assert "marked" in HTML, "(d) without marked, the table renders as pipe characters"


def test_card_audio_files_exist_beside_the_page_and_the_player_is_rendered():
    """#315 round 3: the sutra card carries read-aloud Spanish. A src that does not resolve
    relative to the page is a silent broken player, on disk and in the published artifact."""
    for d in DECKS:
        for i in d["items"]:
            for a in i.get("audio") or []:
                assert (R / a["src"]).is_file(), f"audio missing beside the page: {a['src']}"
    assert 'id="cardAudio"' in HTML and 'el.controls = true' in HTML, "the per-card player is not in the build"
    sutra = next(i for d in DECKS for i in d["items"] if i["id"] == "sutra:satyananda")
    assert len(sutra.get("audio") or []) >= 1, "the sutra card lost its audio"


def test_lang_parameter_and_no_yajna_reader_name_left():
    """#315 round 4: `?lang=es` must open the page in Spanish and the link panel must emit it;
    and the page must call itself Sutra Reader everywhere the LNMY template said Yajna Reader
    (info panel, feedback JSON, flag line) — the owner found the info icon still saying Yajna."""
    assert 'Q.get("lang")' in HTML and 'out.push("lang=es")' in HTML, "the lang parameter is not wired"
    assert "Yajna Reader" not in HTML, "a 'Yajna Reader' string survived in the built page"


# ---- #316 round 1: decks.json gains a sutra level -------------------------------------------

# The sha256 of the ORIGINAL flat decks array (json.dumps, ensure_ascii=False, sort_keys=True),
# captured before the #316 migration moved it under sutras[0]["decks"]. A migration that drops,
# reorders keys in a way that changes content, or mutates one character of any card's md/md_es
# changes this digest -- the whole point of (e).
_PRE_MIGRATION_DECKS_SHA256 = "a22bf44167f34087202ae0d9e382609e81272b8ba47b5fdf4b1dabe6f73306f3"


def test_sutras_level_exists_with_the_owners_id_and_sanskrit():
    """(e) decks.json must carry a "sutras" list, not a bare "decks" list, and the first (only)
    sutra must be II.42 with its label and the sutra's own Sanskrit line."""
    assert isinstance(SUTRAS, list) and len(SUTRAS) >= 1
    s = SUTRAS[0]
    assert s["id"] == "2.42"
    assert "Santo" in s["label"]
    assert s["sanskrit"] == "santoṣād anuttamaḥ sukha-lābhaḥ"
    assert isinstance(s["decks"], list) and s["decks"], "the sutra must carry its decks"


def test_the_migration_moved_the_decks_array_byte_identical():
    """(e) THE SILENT MIGRATION. Proves the move was pure JSON restructuring: hashing the exact
    decks array now sitting under sutras[0] must reproduce the digest of the pre-#316 file."""
    got = hashlib.sha256(
        json.dumps(SUTRAS[0]["decks"], ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    assert got == _PRE_MIGRATION_DECKS_SHA256, "(e) card text changed during the sutras migration"


def _load_build():
    import importlib.util
    spec = importlib.util.spec_from_file_location("santosha_build", R / "build.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_accepts_the_legacy_flat_decks_shape_too(tmp_path):
    """(e) build.py must accept BOTH the new {"sutras": [...]} shape and an old bare
    {"decks": [...]} file (one implicit sutra) -- so a legacy decks.json never hard-fails a
    build. Built against a minimal flat fixture, never the real corpus-derived decks.json."""
    mod = _load_build()
    flat = {"decks": [{"id": "d1", "kind": "sutra", "short": "d1", "attributed": "", "items": [
        {"id": "c1", "title": "T", "md": "**hi**", "book": "B", "attributed": "", "author": "A",
         "year": "2020", "page": "1", "url": "", "exact": True, "speaker": "", "theme": "",
         "why": "", "note": "", "source_file": "", "words": 1},
    ]}]}
    (tmp_path / "decks.json").write_text(json.dumps(flat, ensure_ascii=False), "utf-8")
    (tmp_path / "config.json").write_text((R / "config.json").read_text("utf-8"), "utf-8")
    (tmp_path / "template.html").write_text((R / "template.html").read_text("utf-8"), "utf-8")
    out = mod.build(tmp_path / "r.html", here=tmp_path)
    html = out.read_text("utf-8")
    assert '"sutras":[' in html.replace(" ", ""), "(e) the page payload must always carry sutras"
    assert "__PAYLOAD_JSON__" not in html


# ---- #316 round 2: the sutra strip, above the tabs -------------------------------------------

def test_sutra_strip_sits_above_the_tabs_and_renders_with_one_sutra():
    """(f) THE STRIP NOBODY NOTICES. One segment per sutra, styled with the progress bar's own
    "seg" tokens (no new colours), placed before nav.tabs in the markup so it reads as a level
    above the tab row -- and present even when there is only one sutra to show."""
    assert 'id="sutraStrip"' in HTML
    assert HTML.index('id="sutraStrip"') < HTML.index('id="tabs"'), "(f) the strip must precede nav.tabs"
    for s in SUTRAS:
        assert s["label"] in HTML, f"(f) sutra {s['id']} label missing from the build"


def test_sutra_navigation_keyboard_url_param_and_scoped_state():
    """(f) `[` / `]` step between sutras; `?sutra=<id>` is read on load and re-emitted by
    paramString(); and favourites + position memory are namespaced by sutra id so switching
    sutras cannot leak one sutra's state into another's."""
    assert 'e.key === "["' in HTML, "(f) the [ shortcut is not wired"
    assert 'e.key === "]"' in HTML, "(f) the ] shortcut is not wired"
    assert 'Q.get("sutra")' in HTML, "(f) the sutra URL parameter is not read on load"
    assert '"sutra=" +' in HTML, "(f) paramString() does not emit sutra="
    assert '"-fav"' in HTML, "(f) favourites are not namespaced by sutra id"


def test_reference_strip_names_the_real_host_of_the_link():
    """#315 round 5 (owner): the Osho card said 'satyamyogaprasad.net' while its link opened
    oshofragrance.org. The strip must derive the host from the url, never hardcode one."""
    assert '"satyamyogaprasad.net → p."' not in HTML, "the host is still hardcoded in the reference strip"
    assert "new URL(it.url).hostname" in HTML


def test_swipe_turns_cards_without_stealing_scroll_or_widgets():
    """#317 (owner, 2026-09-16): swiping on a phone did nothing — neither reader listened for a
    horizontal drag. Left = next, right = previous, through move(). The guards are what make it
    safe: vertical scrolling stays with the browser, a drag on the audio player / a link / a form
    field / the etymology table belongs to that element, and Edit mode reorders rather than pages."""
    assert "#317: swipe" in HTML, "the swipe handler is not in the build"
    js = HTML.split("#317: swipe left / right on the card", 1)[1].split("})();", 1)[0]
    assert 'el.addEventListener("touchstart"' in js and 'el.addEventListener("touchend"' in js
    assert "move(dx < 0 ? 1 : -1)" in js, "swipe direction is not wired to move()"
    assert "SWIPE_RATIO * Math.abs(dy)" in js, "a vertical drag could turn the page"
    assert 'audio,a,button,input,textarea,select,table' in js, "a drag on a widget is not excluded"
    assert 'classList.contains("edit-on")' in js, "swipe is live in Edit mode"
    assert "#card{touch-action:pan-y}" in HTML, "vertical scrolling is not left to the browser"
