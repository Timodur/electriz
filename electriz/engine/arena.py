"""Arène : fait jouer deux joueurs l'un contre l'autre et mesure le score.

Chaque ouverture (quelques coups aléatoires) est jouée deux fois, en échangeant
les couleurs, pour qu'aucun camp ne soit favorisé.

Exemples :
    python -m electriz.engine.arena electriz:3 electriz:4 --parties 20
    python -m electriz.engine.arena electriz:3 stockfish:1350 --parties 10

Joueurs :
    electriz:N   Electriz, alpha-bêta à la profondeur N
    stockfish:E  Stockfish bridé à E Elo (UCI_LimitStrength), nécessite --stockfish
"""
import argparse
import math
import os
import random
import shutil
import time

import chess
import chess.engine
import chess.pgn

from .search import Engine

COUPS_OUVERTURE = 4        # demi-coups aléatoires au début de chaque ouverture
MAX_DEMI_COUPS = 300       # au-delà, la partie est déclarée nulle
CHEMIN_STOCKFISH = os.path.expanduser("~/Applications/stockfish/stockfish")


class JoueurElectriz:
    def __init__(self, profondeur):
        self.nom = f"Electriz p{profondeur}"
        self.profondeur = profondeur
        self.engine = Engine()

    def jouer(self, board):
        return self.engine.chercher(board, self.profondeur)[0]

    def fermer(self):
        pass


class JoueurStockfish:
    def __init__(self, chemin, elo, temps):
        self.engine = chess.engine.SimpleEngine.popen_uci(chemin)
        mini = self.engine.options["UCI_Elo"].min
        maxi = self.engine.options["UCI_Elo"].max
        self.elo = max(mini, min(maxi, elo))
        self.engine.configure({"UCI_LimitStrength": True, "UCI_Elo": self.elo})
        self.nom = f"Stockfish {self.elo}"
        self.limite = chess.engine.Limit(time=temps)

    def jouer(self, board):
        return self.engine.play(board, self.limite).move

    def fermer(self):
        self.engine.quit()


def creer_joueur(spec, args):
    genre, _, valeur = spec.partition(":")
    if genre == "electriz":
        return JoueurElectriz(int(valeur or 3))
    if genre == "stockfish":
        chemin = args.stockfish or shutil.which("stockfish") or CHEMIN_STOCKFISH
        if not os.path.exists(chemin):
            raise SystemExit(f"Stockfish introuvable ({chemin}). Utilise --stockfish CHEMIN.")
        return JoueurStockfish(chemin, int(valeur or 1350), args.temps)
    raise SystemExit(f"Joueur inconnu : {spec} (attendu electriz:N ou stockfish:ELO)")


def ouverture_aleatoire(rng):
    """Position après quelques coups aléatoires (sans partie déjà finie)."""
    while True:
        board = chess.Board()
        for _ in range(COUPS_OUVERTURE):
            board.push(rng.choice(list(board.legal_moves)))
        if not board.is_game_over():
            return board


def jouer_partie(blancs, noirs, depart):
    """Joue une partie. Renvoie (board, résultat) avec résultat '1-0', '0-1' ou '1/2-1/2'."""
    board = depart.copy()
    joueurs = {chess.WHITE: blancs, chess.BLACK: noirs}
    while not board.is_game_over(claim_draw=True) and board.ply() < MAX_DEMI_COUPS:
        board.push(joueurs[board.turn].jouer(board))
    resultat = board.result(claim_draw=True)
    return board, ("1/2-1/2" if resultat == "*" else resultat)


def elo_estime(score):
    """Écart d'Elo correspondant à un score moyen (0 < score < 1)."""
    if score <= 0 or score >= 1:
        return None
    return -400 * math.log10(1 / score - 1)


def pgn_de(board, blancs, noirs, resultat):
    partie = chess.pgn.Game.from_board(board)
    partie.headers.update({"White": blancs, "Black": noirs, "Result": resultat})
    return partie


def main():
    p = argparse.ArgumentParser(description="Arène Electriz")
    p.add_argument("joueur_a", help="ex : electriz:3")
    p.add_argument("joueur_b", help="ex : electriz:4 ou stockfish:1350")
    p.add_argument("--parties", type=int, default=10, help="nombre de parties (arrondi au pair)")
    p.add_argument("--graine", type=int, default=None, help="graine des ouvertures (reproductible)")
    p.add_argument("--stockfish", help="chemin vers l'exécutable Stockfish")
    p.add_argument("--temps", type=float, default=0.1, help="secondes par coup pour Stockfish")
    p.add_argument("--pgn", help="fichier où sauvegarder les parties")
    args = p.parse_args()

    rng = random.Random(args.graine)
    a, b = creer_joueur(args.joueur_a, args), creer_joueur(args.joueur_b, args)
    paires = max(1, args.parties // 2)
    points_a, victoires, nulles, defaites = 0.0, 0, 0, 0
    parties_pgn = []
    debut = time.perf_counter()

    try:
        for i in range(paires):
            depart = ouverture_aleatoire(rng)
            for a_blanc in (True, False):
                blancs, noirs = (a, b) if a_blanc else (b, a)
                board, res = jouer_partie(blancs, noirs, depart)
                gain_blancs = {"1-0": 1.0, "0-1": 0.0, "1/2-1/2": 0.5}[res]
                pts = gain_blancs if a_blanc else 1.0 - gain_blancs
                points_a += pts
                victoires += pts == 1.0
                nulles += pts == 0.5
                defaites += pts == 0.0
                parties_pgn.append(pgn_de(board, blancs.nom, noirs.nom, res))
                print(f"partie {len(parties_pgn):3}  {blancs.nom} - {noirs.nom}  {res:7}  "
                      f"({board.ply()} demi-coups)")
    except KeyboardInterrupt:
        print("\nInterrompu : résultats partiels.")
    finally:
        a.fermer()
        b.fermer()

    total = victoires + nulles + defaites
    if total == 0:
        return
    score = points_a / total
    elo = elo_estime(score)
    print("-" * 60)
    print(f"{a.nom} contre {b.nom} : +{victoires} ={nulles} -{defaites}  "
          f"score {points_a:g}/{total} ({score:.0%})  [{time.perf_counter() - debut:.0f} s]")
    if elo is None:
        print("Écart d'Elo : indéterminé (score de 0 % ou 100 %, jouer plus de parties)")
    else:
        print(f"Écart d'Elo estimé de {a.nom} : {elo:+.0f}  (très approximatif si peu de parties)")

    if args.pgn:
        with open(args.pgn, "w", encoding="utf-8") as f:
            for partie in parties_pgn:
                print(partie, file=f, end="\n\n")
        print(f"Parties sauvegardées dans {args.pgn}")


if __name__ == "__main__":
    main()
