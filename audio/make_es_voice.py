"""Spanish voice of the Satyananda II.42 translation (#315) — edge-tts, the real-time-translation
repo's own Spanish voice (es-ES-ElviraNeural, scripts/voice/srt_to_spanish.py), read slowly.

Run with that repo's venv (edge-tts lives there):
  /c/Users/kaanchan/Projects/AI/real-time-translation/.venv/Scripts/python.exe events/santosha-pys-2-42-2026-09/reader/audio/make_es_voice.py
"""
import asyncio
import pathlib

import edge_tts

HERE = pathlib.Path(__file__).resolve().parent

# The Spanish of card sutra:satyananda (decks.json md_es), read as prose: the sutra sentence, then
# the three commentary paragraphs. Pauses come from the paragraph breaks.
TEXT = """De la práctica del contentamiento proviene una felicidad insuperable.

El contentamiento es una de las reglas fijas para el aspirante espiritual que toma muy en serio el aspecto superior del yoga y la realización. Es imposible que quien está insatisfecho consigo mismo, o con cualquier otra cosa de la vida, realice la conciencia superior.

La insatisfacción es uno de los grandes velos de avidya, y por eso debe eliminarse, porque causa muchos complejos indeseables y produce un estado de enfermedad psíquica; y si la mente está enferma, ninguna sadhana es posible.

Quien quiera alcanzar la meditación debe practicar yama y niyama. La conciencia en la meditación debe quedar libre de todos los errores mentales, velos y complejos; por eso hay que practicar santosha, el contentamiento. La felicidad que de ello proviene no tiene igual. Como resultado, uno puede ir muy profundo en la meditación. Sin contentamiento entran en juego distintos complejos mentales, y esa persona no es apta para la meditación."""

TAKES = [
    ("santosha-ii42-es-elvira.mp3", "es-ES-ElviraNeural", "-12%", "+0Hz"),   # Castilian, the repo's default voice
    ("santosha-ii42-es-dalia.mp3", "es-MX-DaliaNeural", "-12%", "+0Hz"),     # Latin-American alternative
]


async def main():
    (HERE / "santosha-ii42-es.txt").write_text(TEXT + "\n", encoding="utf-8", newline="\n")
    for name, voice, rate, pitch in TAKES:
        out = HERE / name
        await edge_tts.Communicate(TEXT, voice, rate=rate, pitch=pitch).save(str(out))
        print(f"{out.name}: {out.stat().st_size:,} bytes  ({voice}, rate {rate})")


asyncio.run(main())
