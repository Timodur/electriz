# electriz

Moteur d'échecs en Python, basé sur la bibliothèque [python-chess](https://python-chess.readthedocs.io/).

## État actuel

- **Évaluation** : matériel + tables pièce-case de la
  [Simplified Evaluation Function](https://www.chessprogramming.org/Simplified_Evaluation_Function)
  (table du roi milieu de partie / finale).
- **Recherche** : [minimax](https://fr.wikipedia.org/wiki/Algorithme_minimax) avec
  [élagage alpha-bêta](https://fr.wikipedia.org/wiki/%C3%89lagage_alpha-b%C3%AAta)
  et tri des coups [MVV-LVA](https://www.chessprogramming.org/MVV-LVA) ; détection des mats et des nulles.
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
python electriz.py                                   # jouer
python -m pytest                                     # tests
python -m src.downloader MagnusCarlsen --contact moi@example.com
python -m src.parser data/raw/MagnusCarlsen_all.pgn --max-games 100
```

## Structure

```text
electriz/
├── electriz.py            # point d'entrée (jeu en console)
├── src/
│   ├── engine/evaluation.py   # évaluation + recherche alpha-bêta
│   ├── downloader.py          # API Chess.com -> data/raw/*.pgn
│   ├── parser.py              # PGN / PGN.zst -> positions FEN
│   ├── uci/                   # (à faire) protocole UCI
│   ├── nnue/, train.py        # (à faire) réseau d'évaluation
│   └── tools/bench.py         # (à faire) benchmark nœuds/s
├── tests/                 # pytest
└── data/                  # non versionné
```

## Licence

BSD 3-Clause — voir [LICENSE](LICENSE).

Copyright (c) 2026, Timothé DURAND
