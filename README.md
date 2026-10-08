# electriz

<p align="center"><img src="assets/logo.svg" width="180" alt="Logo Electriz"></p>

Moteur d'échecs en Python, basé sur la bibliothèque [python-chess](https://python-chess.readthedocs.io/).

## État actuel

- **Évaluation** : matériel + tables pièce-case de la
  [Simplified Evaluation Function](https://www.chessprogramming.org/Simplified_Evaluation_Function)
  (table du roi milieu de partie / finale).
- **Recherche** : [minimax](https://fr.wikipedia.org/wiki/Algorithme_minimax) avec
  [élagage alpha-bêta](https://fr.wikipedia.org/wiki/%C3%89lagage_alpha-b%C3%AAta)
  et tri des coups [MVV-LVA](https://www.chessprogramming.org/MVV-LVA) ; détection des mats et des nulles.
- **Protocole UCI** : utilisable dans Cute Chess, Arena, etc. Approfondissement itératif avec limite de
  temps (`go depth`, `movetime`, `wtime`/`btime`) — voir [Mode UCI](#mode-uci).
- **Jeu en console** : IA contre IA ou humain contre IA (échiquier redessiné dans `echiquier.svg`),
  parties sauvegardées en PGN dans `data/raw/parties/`.
- **Données** : téléchargement des parties d'un joueur Chess.com, lecture des bases Lichess `.pgn.zst`.

| Niveau | IA |
|---|---|
| 1 | coup aléatoire |
| 2 | capture si possible |
| 3 | meilleur coup à 1 demi-coup |
| 4 | alpha-bêta profondeur 3 |
| 5 | alpha-bêta profondeur 4 |

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

```bash
python -m electriz     # jouer (IA vs IA ou humain vs IA)
python -m electriz.uci # mode UCI (Cute Chess, Arena...)
python -m pytest       # tests
python -m electriz.tools.bench --depth 4   # benchmark (noeuds/s)
python -m electriz.datasets.downloader MagnusCarlsen --contact moi@example.com
python -m electriz.datasets.parser data/raw/MagnusCarlsen_all.pgn --max-games 100
```

## Mode UCI

[UCI](https://backscattering.de/chess/uci/) est le protocole standard entre un moteur et une interface
graphique. Le script `electriz-uci.sh` (à la racine) lance le moteur avec le bon environnement Python.

### Brancher sur Cute Chess

1. Installer [Cute Chess](https://github.com/cutechess/cutechess/releases) (AppImage : `chmod +x` puis lancer ;
   pas de paquet `cutechess` sous Debian).
2. `Tools > Settings > Engines > +` :
   - **Name** : `Electriz`
   - **Command** : chemin complet vers `electriz-uci.sh` (ex. `/home/timothe/Documents/electriz/electriz-uci.sh`)
   - **Working directory** : la racine du projet
   - **Protocol** : `UCI`
3. `Game > New` pour jouer contre Electriz, ou `Tools > Tournaments` pour faire jouer deux moteurs.
4. Pour se mesurer à [Stockfish](https://stockfishchess.org/), l'ajouter de la même façon puis le brider
   (`UCI_LimitStrength` = true, `UCI_Elo` = 1350, ou `Skill Level` = 0), sinon Electriz perdra toujours.

### Tester à la main

```bash
python -m electriz.uci
```

| Commande | Réponse |
|---|---|
| `uci` | `id name Electriz`, `id author ...`, `uciok` |
| `isready` | `readyok` |
| `ucinewgame` | repart d'une partie vierge |
| `position startpos moves e2e4 e7e5` | place la position (ou `position fen <FEN> moves ...`) |
| `go depth 4` | cherche à profondeur 4, puis `bestmove ...` |
| `go movetime 1000` | cherche ~1 s |
| `go wtime 60000 btime 60000 winc 0 binc 0` | gère son temps selon les pendules |
| `quit` | quitte |

Exemple : `printf 'position startpos moves e2e4\ngo depth 4\nquit\n' | python -m electriz.uci`

## Structure

```text
.
├── electriz-uci.sh           # lanceur pour Cute Chess / Arena
├── electriz/                 # paquet Python (python -m electriz)
│   ├── __main__.py
│   ├── jeu.py                # parties en console, sauvegarde PGN
│   ├── engine/
│   │   ├── evaluation.py
│   │   ├── search.py
│   │   ├── arena.py
│   │   └── selfplay.py
│   ├── datasets/
│   │   ├── downloader.py     # API Chess.com -> data/raw/*.pgn
│   │   └── parser.py         # PGN / PGN.zst -> positions FEN
│   ├── uci/
│   │   ├── __main__.py       # python -m electriz.uci
│   │   └── loop.py           # protocole UCI
│   ├── nnue/
│   │   ├── model.py
│   │   ├── eval.py
│   │   └── train.py
│   └── tools/bench.py
├── tests/
│   ├── engine/
│   │   ├── conftest.py
│   │   ├── positions.py
│   │   ├── test_evaluation.py
│   │   └── test_search.py
│   └── test_uci.py
├── assets/
│   ├── logo.svg
│   ├── logo-2x2.svg
│   └── sources/
└── data/
    ├── raw/                  # parties téléchargées
    └── processed/            # positions FEN
```

## Licence

BSD 3-Clause — voir [LICENSE](LICENSE).

Copyright (c) 2026, Timothé DURAND
