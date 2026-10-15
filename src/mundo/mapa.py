"""O mapa do nivel: um JSON com a lista de objetos, lido e gravado pelo jogo.

O formato e o mesmo que o mapmaker (`Desktop/mapmaker`) grava e le: cada objeto
tem `tipo`, um retangulo em coordenadas de mundo e, quando faz sentido, uma
`direcao`. Quem monta as entidades a partir disso e `mundo/nivel.py`.

    {"versao": 1, "nome": "nivel1", "largura_mundo": 3830, "chao_y": 656,
     "objetos": [{"tipo": "chao", "x": 0, "y": 656, "w": 3830, "h": 90}, ...]}

O jogo procura o mapa nesta ordem: `METALMAX_MAPA`, o arquivo do repo e, se nada
disso abrir, um chao reto de emergencia — nivel quebrado nunca derruba o jogo.
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from src.entidades.itens import Chave, Moeda, Pedra
from src.entidades.obstaculos import BlocoGrama, CaixaSolida, Espinhos, Mola
from src.entidades.ponte import Plataforma
from src.mundo.portao import Porta
from src.ui.config import CHAO_Y, LARGURA_MUNDO, RAIZ

VERSAO = 1
TIPOS = ("chao", "plataforma", "bloco", "caixa", "espinho", "mola", "moeda", "pedra", "chave", "porta")
DIRECOES = ("cima", "baixo", "esquerda", "direita")
MAPA_DO_REPO = ("assets", "mapas", "nivel1.json")
VARIAVEL_AMBIENTE = "METALMAX_MAPA"

# tamanho de nascenca de cada peca: (largura, altura). O editor usa isso ao
# colocar uma peca nova; a chave, a moeda e a pedra tem tamanho proprio na
# entidade, mas o retangulo aqui e o que o editor desenha e o que o mapa grava.
PADROES = {
    "chao": (520, 90),
    "plataforma": (170, 12),
    "bloco": (60, 60),
    "caixa": (30, 30),
    "espinho": (56, 16),
    "mola": (32, 28),
    "moeda": (26, 26),
    "pedra": (26, 26),
    "chave": (22, 26),
    "porta": (72, 104),
}

_MINIMO = 8        # sanidade: nada de retangulo de tamanho zero
_MAXIMO = 3830     # nem de retangulo do tamanho do mundo


def construir(o: dict):
    """Cria a entidade de um objeto do mapa: devolve (lista de destino, entidade).

    `nivel.py` usa isso para montar a fase e o mapmaker usa para desenhar a
    previa — assim a peca no editor e a peca no jogo sao a mesma, desenhada pelo
    mesmo codigo.
    """
    tipo = o["tipo"]
    x, y, w, h = o["x"], o["y"], o["w"], o["h"]
    direcao = o.get("direcao", "cima")
    if tipo == "chao":
        return "plataformas", Plataforma(x, y, w, h, chao=True)
    if tipo == "plataforma":
        return "plataformas", Plataforma(x, y, w, h)
    if tipo == "bloco":
        return "obstaculos", BlocoGrama(x, y, w, h)
    if tipo == "caixa":
        return "obstaculos", CaixaSolida(x, y, w, h)
    if tipo == "espinho":
        return "obstaculos", Espinhos(x, y, w, h, direcao)
    if tipo == "mola":
        return "molas", Mola(x, y, w, h, direcao)
    if tipo == "moeda":
        return "itens", Moeda(x, y)
    if tipo == "pedra":
        return "itens", Pedra(x, y)
    if tipo == "chave":
        return "itens", Chave(x, y)
    if tipo == "porta":
        return "porta", Porta(x, y, w, h)
    return None, None


def _do_ambiente(nome: str) -> Path | None:
    """Le uma variavel de ambiente como caminho, tolerando aspas.

    No Windows e comum escrever `set METALMAX_MAPA="C:\\mapa.json"`, e as aspas
    ficam dentro do valor: sem tirar, o caminho nao existe.
    """
    valor = os.environ.get(nome, "").strip().strip('"').strip("'")
    return Path(valor).expanduser() if valor else None


def caminho_padrao() -> Path:
    """`METALMAX_MAPA` quando existir; senao o mapa que vem no repo."""
    escolhido = _do_ambiente(VARIAVEL_AMBIENTE)
    if escolhido is not None:
        return escolhido
    return RAIZ.joinpath(*MAPA_DO_REPO)


def padrao() -> dict:
    """Mapa de emergencia: um chao reto, para o jogo nunca abrir vazio."""
    return {
        "versao": VERSAO,
        "nome": "vazio",
        "largura_mundo": LARGURA_MUNDO,
        "chao_y": CHAO_Y,
        "objetos": [{"tipo": "chao", "x": 0, "y": CHAO_Y, "w": LARGURA_MUNDO, "h": 90}],
    }


def objeto(tipo: str, x: int, y: int, w: int, h: int, direcao: str | None = None) -> dict:
    """Monta um objeto do mapa, ja no formato de saida."""
    item = {"tipo": tipo, "x": int(x), "y": int(y), "w": int(w), "h": int(h)}
    if direcao is not None:
        item["direcao"] = direcao
    return item


def normalizar(mapa: dict) -> dict:
    """Devolve o mapa com as chaves garantidas e os objetos saneados.

    Objeto de tipo desconhecido, retangulo degenerado ou direcao invalida e
    descartado: o jogo prefere um mapa menor do que um mapa que quebra.
    """
    if not isinstance(mapa, dict):
        return padrao()
    objetos = []
    for bruto in mapa.get("objetos", []):
        if not isinstance(bruto, dict) or bruto.get("tipo") not in TIPOS:
            continue
        try:
            x, y = int(bruto["x"]), int(bruto["y"])
            w, h = int(bruto["w"]), int(bruto["h"])
        except (KeyError, TypeError, ValueError):
            continue
        if not (_MINIMO <= w <= _MAXIMO and _MINIMO <= h <= _MAXIMO):
            continue
        direcao = bruto.get("direcao")
        if direcao not in DIRECOES:
            direcao = "cima"
        objetos.append(objeto(bruto["tipo"], x, y, w, h, direcao if "direcao" in bruto else None))
    nascimento = {}
    if isinstance(mapa.get("nascer"), dict):
        try:
            nascimento = {"x": int(mapa["nascer"]["x"]), "y": int(mapa["nascer"]["y"])}
        except (KeyError, TypeError, ValueError):
            nascimento = {}
    saida = {
        "versao": VERSAO,
        "nome": str(mapa.get("nome", "mapa")),
        "largura_mundo": int(mapa.get("largura_mundo", LARGURA_MUNDO)),
        "chao_y": int(mapa.get("chao_y", CHAO_Y)),
        "objetos": objetos,
    }
    if nascimento:
        saida["nascer"] = nascimento
    return saida


def carregar(caminho: str | Path | None = None) -> dict:
    """Le o mapa do disco; qualquer problema cai no mapa de emergencia."""
    try:
        return normalizar(json.loads(Path(caminho or caminho_padrao()).read_text(encoding="utf-8")))
    except (OSError, ValueError):
        return padrao()


def salvar(mapa: dict, caminho: str | Path) -> Path:
    """Grava o mapa (saneado) e devolve o caminho usado."""
    destino = Path(caminho).expanduser()
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(json.dumps(normalizar(mapa), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return destino
