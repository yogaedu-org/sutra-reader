# -*- coding: utf-8 -*-
"""#315 — the Santosha reader (events/santosha-pys-2-42-2026-09/reader), built from the corpus.

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
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
# ajna keeps the reader under events/; the public export (scripts/export_sutra_reader.py) puts
# decks.json at the repo root and builds index.html. The same guards run in both trees.
_nested = REPO / "events" / "santosha-pys-2-42-2026-09" / "reader"
R = _nested if (_nested / "decks.json").is_file() else REPO
DECKS = json.loads((R / "decks.json").read_text(encoding="utf-8"))["decks"]
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


def test_reference_strip_names_the_real_host_of_the_link():
    """#315 round 5 (owner): the Osho card said 'satyamyogaprasad.net' while its link opened
    oshofragrance.org. The strip must derive the host from the url, never hardcode one."""
    assert '"satyamyogaprasad.net → p."' not in HTML, "the host is still hardcoded in the reference strip"
    assert "new URL(it.url).hostname" in HTML
