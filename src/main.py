"""Ponto de entrada dentro de `src`.

Deixa a raiz do projeto no caminho para que os imports `from src.ui...`
funcionem tambem quando o jogo e chamado por aqui.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src.ui.jogo import Jogo

if __name__ == "__main__":
    Jogo().rodar()
