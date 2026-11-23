"""Muestra los chunks que armó `uv run ingest build`, para revisarlos antes de publicar.

uv run python dev/show_chunks.py                          resumen: fuente, largo y sección de cada chunk
uv run python dev/show_chunks.py response-times.csv   texto completo de los chunks de una fuente
"""

import os
import sys

from agent.infrastructure.config.settings import Settings
from agent.infrastructure.ingestion.chunks_file import read_chunks

RESET = "\033[0m"
DIM = "\033[2m"
INFO = "\033[1;92m"
LEVEL_COLORS = ["\033[1;36m", "\033[1;33m", "\033[1;35m", "\033[1;32m", "\033[1;34m"]
USE_COLOR = sys.stdout.isatty()
if USE_COLOR and os.name == "nt":
    os.system("")  # en la consola de Windows, esto activa las secuencias de color


def paint(text: str, code: str) -> str:
    return f"{code}{text}{RESET}" if USE_COLOR else text


def color_path(section: str) -> str:
    """Cada nivel de la jerarquía tiene su propio color; el separador ' > ' va atenuado."""
    separator = paint(" > ", DIM)
    levels = section.split(" > ")
    return separator.join(paint(level, LEVEL_COLORS[i % len(LEVEL_COLORS)]) for i, level in enumerate(levels))


settings = Settings()
path = settings.ingest.data_dir / "chunks" / f"{settings.domain}.json"
chunks = read_chunks(path)
if not chunks:
    sys.exit(f"No hay chunks en {path}. Corre primero: uv run ingest build")

if len(sys.argv) > 1:
    for chunk in (candidate for candidate in chunks if candidate.source == sys.argv[1]):
        info = paint(f"({len(chunk.content)} caracteres, vector de {len(chunk.content_vector)})", INFO)
        first_line, _, rest = chunk.content.partition("\n")
        if first_line == chunk.section:
            first_line = color_path(first_line)
        print(f"--- {color_path(chunk.section)}  {info}\n{first_line}\n{rest}\n")
else:
    for chunk in chunks:
        print(f"{chunk.source:40} {len(chunk.content):5}  {chunk.section}")
    print(f"\n{len(chunks)} chunks en {path}")