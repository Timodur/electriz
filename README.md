# electriz

<p align="center"><img src="assets/logo.svg" width="180" alt="Logo Electriz"></p>

Moteur d'échecs en Python, basé sur la bibliothèque [python-chess](https://python-chess.readthedocs.io/).

## État actuel

- **Évaluation** : matériel + tables pièce-case de la
  [Simplified Evaluation Function](https://www.chessprogramming.org/Simplified_Evaluation_Function)
  (table du roi milieu de partie / finale).
- **Recherche** : [minimax](https://fr.wikipedia.org/wiki/Algorithme_minimax) avec
  [élagage alpha-bêta](https://fr.wikipedia.org/wiki/%C3%89lagage_alpha-b%C3%AAta)
  et tri des coups [MVV-LVA](https://www.chessprogramming.org/MVV-LVA) ; détection des mats et des nulles ;
  échéance de temps optionnelle (la recherche s'interrompt proprement).
- **Protocole UCI** : utilisable dans Cute Chess, Arena, etc. Approfondissement itératif avec limite de
  temps (`go depth`, `movetime`, `wtime`/`btime`) — voir [Mode UCI](#mode-uci).
- **Arène** : matchs entre deux joueurs (Electriz à diverses profondeurs, Stockfish bridé) avec ouvertures
  aléatoires, couleurs échangées, score et Elo estimé — voir [Arène](#arène).
- **Jeu en console** : IA contre IA ou humain contre IA (échiquier redessiné dans `echiquier.svg`),
  parties sauvegardées en PGN dans `data/raw/parties/`.
- **Benchmark** : vitesse de recherche en nœuds par seconde.
- **Données** : téléchargement des parties d'un joueur Chess.com, lecture des bases Lichess `.pgn.zst`.

| Niveau | IA |
|---|---|
| 1 | coup aléatoire |
| 2 | capture si possible |
| 3 | meilleur coup à 1 demi-coup |
| 4 | alpha-bêta profondeur 3 |
| 5 | alpha-bêta profondeur 4 |

Les niveaux 1 et 2 utilisent le hasard : deux parties ne sont jamais identiques. Les niveaux 3 à 5 sont
déterministes (même position, même coup), donc rejouent toujours la même partie depuis la position de départ.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Utilisation

Toutes les commandes se lancent depuis la racine du dépôt, venv activé.

```bash
python -m electriz                         # jouer (IA vs IA ou humain vs IA)
python -m electriz.uci                     # mode UCI (Cute Chess, Arena...)
python -m electriz.engine.arena electriz:3 electriz:4 --parties 20   # arène
python -m electriz.tools.bench --depth 4   # benchmark (nœuds/s)
python -m pytest                           # tests
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

Limites actuelles : `go infinite` et `stop` ne sont pas gérés ; la `pv` ne contient que le premier coup.

## Arène

Fait jouer deux joueurs l'un contre l'autre. Chaque ouverture (4 demi-coups aléatoires) est jouée deux fois,
couleurs échangées, pour ne favoriser aucun camp.

```bash
python -m electriz.engine.arena electriz:3 electriz:4 --parties 20
python -m electriz.engine.arena electriz:3 stockfish:1350 --parties 10 --pgn parties.pgn
```

| Joueur | Signification |
|---|---|
| `electriz:N` | Electriz, alpha-bêta à la profondeur N |
| `stockfish:E` | Stockfish bridé à E Elo (`UCI_LimitStrength`) |

| Option | Rôle |
|---|---|
| `--parties N` | nombre de parties (arrondi au pair, défaut 10) |
| `--graine N` | rend les ouvertures reproductibles |
| `--temps S` | secondes par coup pour Stockfish (défaut 0,1) |
| `--stockfish CHEMIN` | exécutable Stockfish (défaut : `stockfish` du PATH, sinon `~/Applications/stockfish/stockfish`) |
| `--pgn FICHIER` | sauvegarde les parties |

La sortie donne le score (+victoires =nulles -défaites) et un écart d'Elo estimé. Il n'est fiable qu'avec
au moins 50 à 100 parties.

## Structure

```text
.
├── electriz-uci.sh           # lanceur pour Cute Chess / Arena
├── electriz/                 # paquet Python (python -m electriz)
│   ├── __main__.py
│   ├── jeu.py                # parties en console, sauvegarde PGN
│   ├── engine/
│   │   ├── evaluation.py     # matériel + tables pièce-case
│   │   ├── search.py         # minimax, alpha-bêta, échéance de temps
│   │   ├── arena.py          # matchs entre joueurs, score, Elo
│   │   └── selfplay.py       # (à faire) génération de parties
│   ├── datasets/
│   │   ├── downloader.py     # API Chess.com -> data/raw/*.pgn
│   │   └── parser.py         # PGN / PGN.zst -> positions FEN
│   ├── uci/
│   │   ├── __main__.py       # python -m electriz.uci
│   │   └── loop.py           # protocole UCI
│   ├── nnue/                 # (à faire) évaluation par réseau de neurones
│   │   ├── model.py
│   │   ├── eval.py
│   │   └── train.py
│   └── tools/bench.py        # benchmark nœuds/s
├── tests/
│   ├── engine/
│   │   ├── conftest.py
│   │   ├── positions.py
│   │   ├── test_evaluation.py
│   │   ├── test_search.py
│   │   └── test_arena.py
│   └── test_uci.py
├── assets/
│   ├── logo.svg
│   ├── logo-2x2.svg
│   └── sources/
└── data/
    ├── raw/                  # parties téléchargées
    └── processed/            # positions FEN
```

## Pistes d'amélioration

1. Recherche de quiescence (captures en fin de recherche) pour supprimer l'effet d'horizon.
2. Table de transposition (hash Zobrist), passage en negamax, coups killers.
3. Évaluation PeSTO, sécurité du roi, structure de pions.
4. UCI : `go infinite` / `stop`, ligne principale complète.
5. Évaluation par réseau de neurones (`electriz/nnue/`).

Chaque modification de la recherche ou de l'évaluation se valide avec l'arène (nouvelle version contre ancienne).

## Licence

BSD 3-Clause — voir [LICENSE](LICENSE).

Copyright (c) 2026, Timothé DURAND
