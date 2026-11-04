"""Persistencia local dos melhores tempos da campanha."""
from __future__ import annotations

import json
from pathlib import Path

from src.ui.config import RAIZ

CAMINHO = RAIZ / "leaderboard.json"
MAXIMO_REGISTROS = 10


def carregar() -> list[dict[str, str]]:
    try:
        dados = json.loads(CAMINHO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    if not isinstance(dados, list):
        return []
    return [
        {"nome": str(item["nome"])[:16], "tempo": str(item["tempo"])}
        for item in dados
        if isinstance(item, dict) and item.get("nome") and item.get("tempo")
    ][:MAXIMO_REGISTROS]


def registrar(nome: str, segundos: float) -> list[dict[str, str]]:
    """Guarda o tempo de conclusão e devolve a classificação atualizada."""
    registros = carregar()
    registros.append({"nome": nome.strip()[:16] or "JOGADOR", "segundos": segundos})
    registros.sort(key=_segundos_registro)
    classificados = [
        {"nome": item["nome"], "tempo": _formatar(_segundos_registro(item))}
        for item in registros[:MAXIMO_REGISTROS]
    ]
    CAMINHO.write_text(json.dumps(classificados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return classificados


def _segundos_registro(item: dict) -> float:
    if "segundos" in item:
        return float(item["segundos"])
    return _tempo_segundos(item["tempo"])


def _tempo_segundos(tempo: str) -> float:
    minutos, segundos = tempo.split(":", 1)
    return int(minutos) * 60 + float(segundos)


def _formatar(segundos: float) -> str:
    minutos, resto = divmod(max(0.0, segundos), 60)
    return f"{int(minutos):02d}:{resto:05.2f}"
