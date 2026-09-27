# METAL MAX

## Rodar o jogo

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```
## Ver a documentação

A documentação é um site estático que já vem compilado em `docs/build/`. Não
precisa de Node, nem de instalar nada.

```bash
python -m http.server -d docs/build 8000
```

Depois abra **http://localhost:8000**. Para derrubar o servidor, `Ctrl+C`.

| Arquivo | O que é |
|---|---|
| `docs/docs/*.md` | o conteúdo, em Markdown |
| `docs/docusaurus.config.js` | configuração do site |
| `docs/Dockerfile` | build em duas etapas: Node compila, nginx serve |
| `docs/build/` | site gerado — versionado no git, são 812 KB |
| `docs/node_modules/` | dependências — ignoradas pelo git |

---


## Estrutura

```
metal-max/
├── main.py                      ponto de entrada: só cria e roda o jogo
├── README.md
├── requirements.txt             pygame-ce
├── .gitignore
├── assets/
│   └── imagens/                 pug.png (sprite sheet) e fundos
├── docs/                        site de documentação (Docusaurus)
└── src/
    ├── main.py                  mesmo jogo, callable por dentro de src/
    ├── assets.py                cache de imagens
    ├── entidades/               os atores do jogo, cada um em seu arquivo
    │   ├── entidade.py          base: posição, hitbox, velocidade
    │   ├── animacao.py          corte das células do sprite sheet
    │   ├── jogador.py           classe Jogador
    │   ├── obstaculos.py        Obstáculo (base) + Espinhos, Caixa
    │   ├── ponte.py             Plataforma + plataforma móvel
    │   ├── itens.py             Coletável (base) + Moeda, Coração, Pedra, Chave
    │   └── inimigos.py          Inimigo (base) + 4 comportamentos
    ├── mundo/
    │   ├── cenario.py           fundo com parallax
    │   ├── camera.py            segue o jogador e recorta o que está fora
    │   ├── fisica.py            colisão e o carregamento pelas plataformas
    │   ├── nivel.py             monta o mapa e resolve as interações
    │   └── portao.py            saída da fase
    └── ui/
        ├── config.py            constantes: janela, física, biomas
        ├── cores.py             paleta, tirada da arte do pug
        ├── jogo.py              classe Jogo: o loop principal
        ├── hud.py               barra de status em uma linha
        ├── menu.py              capa de início
        ├── avisos.py            pausa, controles, vitória
        └── estilo.py            peças de desenho compartilhadas
```

