# Sutra Reader — Patanjali Yoga Sutras, one sutra at a time

**Read it: https://yogaedu-org.github.io/sutra-reader/**

A one-page reader for a talk on a single sutra. First sutra: **II.42 — santoṣād anuttamaḥ
sukha-lābhaḥ** (from contentment, unsurpassed happiness). Every English card is a verbatim excerpt
from a published book of the Satyananda Yoga tradition, with the page it comes from linked on
satyamyogaprasad.net; the Spanish is a translation prepared for the room; the sutra card carries a
read-aloud Spanish recording.

Tabs: **The Sutra** (Swami Satyananda's rendering from *Four Chapters on Freedom*, the Vyāsa-bhāṣya,
Osho) · **Readings** by author · **Stories** · **Quotes** (bilingual) · **Etymology** (the sam- family).

Keys: `←` `→` `space` move · `L` English ↔ Español · `V` live (hide counts and references) ·
`A` auto-advance · `F` full screen · `Esc` stop.

## Rebuild the page

```
python build.py            # decks.json + config.json + template.html -> index.html
python -m pytest tests -q  # the guards
```

| file | role |
|---|---|
| `decks.json` | the content — every card, every deck, in reading order |
| `config.json` | tabs, auto-advance bounds, feature toggles, colour + type tokens |
| `template.html` | the page: markup, CSS, JS, three placeholders the build fills |
| `build.py` | the build (no network, no model) |
| `audio/` | the Spanish recording of the sutra card, and the script that made it (edge-tts) |
| `sources/` | the verbatim page text the sutra card was transcribed from |
| `tests/` | the guards: every card bilingual where required, the sutra tab order, the etymology table, the audio beside the page |

Card text is verbatim from the source books; nothing on a card is paraphrased. Corrections and
suggestions: open an issue.

## Licence

Code: MIT. Quoted passages remain the copyright of their publishers (Yoga Publications Trust /
Bihar School of Yoga / Sannyasa Peeth) and are reproduced for study, with the source page linked.
