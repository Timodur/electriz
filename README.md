<p align="center"><img src="assets/logo.svg" width="180" alt="Logo Electriz"></p>

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
python -m src          # jouer (IA vs IA ou humain vs IA)
python -m pytest       # tests
python -m src.datasets.downloader MagnusCarlsen --contact moi@example.com
python -m src.datasets.parser data/raw/MagnusCarlsen_all.pgn --max-games 100
```

## Structure

```text
electriz/
├── src/
│   ├── __main__.py            
│   ├── jeu.py            # parties en console, sauvegarde PGN
│   ├── engine/
│   │   ├── evaluation.py      
│   │   ├── search.py          
│   │   ├── arena.py           
│   │   └── selfplay.py        
│   ├── datasets/
│   │   ├── downloader.py # API Chess.com -> data/raw/*.pgn
│   │   └── parser.py     # PGN / PGN.zst -> positions FEN
│   ├── uci/loop.py
│   ├── nnue/
│   │   ├── model.py
│   │   ├── eval.py
│   │   └── train.py
│   └── tools/bench.py 
├── tests/
│   └── engine/
│       ├── evaluation.py
│       ├── search.py
│       ├── arena.py
│       └── selfplay.py
├── assets/
│   ├── logo.svg               
│   ├── logo-2x2.svg           
│   └── sources/              
└── data/
    ├── raw/               # parties téléchargées
    └── processed/         # positions FEN
```

## Licence

BSD 3-Clause — voir [LICENSE](LICENSE).

Copyright (c) 2026, Timothé DURAND
