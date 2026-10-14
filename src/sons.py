"""Sonoplastia em codigo: o projeto nao usa arquivo de audio.

Sao dois sons, ambos montados amostra a amostra: o **estouro** da morte (ruido
filtrado, estalo no ataque e um assobio que cai de tom) e o **boing** da mola
(tom que sobe depressa, tremendo como mola). Cada um vira um `Sound` uma unica
vez; a taxa e os canais saem do mixer que ja estiver ligado.

Sem placa de som — ou com o mixer falhando — o jogo segue mudo, sem quebrar.
"""
from __future__ import annotations

import array
import math
import random

import pygame

DURACAO_EXPLOSAO = 0.5       # segundos
VOLUME_EXPLOSAO = 0.6        # fica um pouco abaixo do teto: a morte nao assusta
_QUEDA_VOLUME = 9.0          # envelope geral: some ~35 dB ate o fim
_QUEDA_ESTALO = 40.0         # o estalo do ataque e quase instantaneo
_TOM_ALTO = 900.0            # o assobio cai deste tom...
_TOM_BAIXO = 90.0            # ...ate este
_QUEDA_TOM = 7.0

DURACAO_MOLA = 0.34          # segundos
VOLUME_MOLA = 0.5
_MOLA_TOM = 180.0            # o boing sobe deste tom...
_MOLA_SUBIDA = 900.0         # ...ate este, depressa
_MOLA_SUBE = 9.0             # rapidez da subida
_MOLA_VIBRATO = 26.0         # Hz do tremor de mola
_MOLA_TREMOR = 0.22          # profundidade do tremor
_QUEDA_MOLA = 7.0            # o boing some depressa, mas nao num estalo

# Cache dos `Sound` gerados; cada um nasce no primeiro toque, ja com o volume.
_sons: dict[str, pygame.mixer.Sound] = {}
_disponivel: bool | None = None


def _abrir_mixer() -> bool:
    """Liga o mixer uma vez. Devolve False quando nao ha audio nenhum."""
    global _disponivel
    if _disponivel is None:
        try:
            pygame.mixer.init()
            _disponivel = pygame.mixer.get_init() is not None
        except pygame.error:
            _disponivel = False
    return _disponivel


def _embalar(amostras: array.array, canais: int) -> bytes:
    """Intercala a amostra em todos os canais do mixer.

    Nao basta repetir o array: `[a, b] * 2` vira `[a, b, a, b]`, que o mixer le
    como dois quadros — o som saia com metade da duracao e o tom dobrado.
    """
    if canais <= 1:
        return amostras.tobytes()
    dados = array.array(amostras.typecode, bytes(len(amostras) * canais * amostras.itemsize))
    for canal in range(canais):
        dados[canal::canais] = amostras
    return dados.tobytes()


def _gerar_explosao(taxa: int, bits: int, canais: int) -> pygame.mixer.Sound:
    total = int(taxa * DURACAO_EXPLOSAO)
    ruido_grave = 0.0
    fase = 0.0
    if bits == 8:
        amostras = array.array("B")      # 8 bits sem sinal, 128 = silencio
    else:
        amostras = array.array("h")      # 16 bits com sinal
    for i in range(total):
        t = i / taxa
        ruido_grave += (random.uniform(-1.0, 1.0) - ruido_grave) * 0.08   # media corrida = estrondo
        estalo = random.uniform(-1.0, 1.0) * math.exp(-_QUEDA_ESTALO * t)
        fase += math.tau * (_TOM_BAIXO + _TOM_ALTO * math.exp(-_QUEDA_TOM * t)) / taxa
        assobio = math.sin(fase)
        valor = (ruido_grave * 1.5 + estalo * 0.6 + assobio * 0.45) * math.exp(-_QUEDA_VOLUME * t)
        valor = math.tanh(valor * 1.8) * 0.9   # satura: deixa o estouro gordo, sem clipar
        if bits == 8:
            amostras.append(round(valor * 127) + 128)
        else:
            amostras.append(int(valor * 32767))
    return pygame.mixer.Sound(buffer=_embalar(amostras, canais))


def _gerar_mola(taxa: int, bits: int, canais: int) -> pygame.mixer.Sound:
    """Boing de mola: um tom que sobe depressa e treme enquanto sobe.

    O tremor (vibrato de 26 Hz) e o que faz soar "molenga"; sem ele o mesmo
    tom subindo soa como assobio.
    """
    total = int(taxa * DURACAO_MOLA)
    fase = 0.0
    if bits == 8:
        amostras = array.array("B")
    else:
        amostras = array.array("h")
    for i in range(total):
        t = i / taxa
        tom = _MOLA_TOM + _MOLA_SUBIDA * (1.0 - math.exp(-_MOLA_SUBE * t))
        tremor = 1.0 + _MOLA_TREMOR * math.sin(math.tau * _MOLA_VIBRATO * t)
        fase += math.tau * tom * tremor / taxa
        estalo = random.uniform(-1.0, 1.0) * math.exp(-60.0 * t) * 0.4
        valor = math.tanh((math.sin(fase) * 0.9 + estalo) * 1.4) * math.exp(-_QUEDA_MOLA * t) * 0.9
        if bits == 8:
            amostras.append(round(valor * 127) + 128)
        else:
            amostras.append(int(valor * 32767))
    return pygame.mixer.Sound(buffer=_embalar(amostras, canais))


# nome -> (gerador, volume). O `Sound` nasce no primeiro toque, ja no volume.
_DEFINICOES = {
    "explosao": (_gerar_explosao, VOLUME_EXPLOSAO),
    "mola": (_gerar_mola, VOLUME_MOLA),
}


def _tocar(nome: str) -> None:
    """Gera (uma vez) e toca; sem mixer, nao faz nada."""
    if not _abrir_mixer():
        return
    if nome not in _sons:
        gerar, volume = _DEFINICOES[nome]
        taxa, tamanho, canais = pygame.mixer.get_init()
        som = gerar(taxa, abs(tamanho), canais)
        som.set_volume(volume)
        _sons[nome] = som
    _sons[nome].play()


def explosao() -> None:
    """Estouro do corpo no espinho."""
    _tocar("explosao")


def mola() -> None:
    """Boing da mola que lanca o pug."""
    _tocar("mola")
