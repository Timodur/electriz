"""Protocole UCI : permet de brancher Electriz sur Cute Chess, Arena, etc.

Spécification : https://backscattering.de/chess/uci/
Lancement : python -m electriz.uci
"""
import sys
import time

import chess

from electriz.engine import MATE_SCORE, Engine
from electriz.engine.search import TempsEcoule

NOM = "Electriz"
AUTEUR = "Timothé DURAND"
PROFONDEUR_DEFAUT = 4
PROFONDEUR_MAX = 64


class UCI:
    def __init__(self, entree=None, sortie=None):
        self.entree = entree or sys.stdin
        self.sortie = sortie or sys.stdout
        self.board = chess.Board()
        self.engine = Engine()

    def envoyer(self, texte):
        print(texte, file=self.sortie, flush=True)

    # ------------------------------------------------------------------
    # Boucle principale
    # ------------------------------------------------------------------
    def run(self):
        for ligne in self.entree:
            if not self.traiter(ligne.strip()):
                break

    def traiter(self, ligne):
        """Traite une commande. Renvoie False quand il faut quitter."""
        mots = ligne.split()
        if not mots:
            return True
        cmd, args = mots[0], mots[1:]

        if cmd == "uci":
            self.envoyer(f"id name {NOM}")
            self.envoyer(f"id author {AUTEUR}")
            self.envoyer("uciok")
        elif cmd == "isready":
            self.envoyer("readyok")
        elif cmd == "ucinewgame":
            self.board = chess.Board()
        elif cmd == "position":
            self.position(args)
        elif cmd == "go":
            self.go(args)
        elif cmd == "d":  # debug, pratique à la main
            self.envoyer(str(self.board))
        elif cmd == "quit":
            return False
        return True  # commandes inconnues ignorées, comme le demande la spec

    # ------------------------------------------------------------------
    # position [startpos | fen <fen>] [moves <coup> ...]
    # ------------------------------------------------------------------
    def position(self, args):
        if "moves" in args:
            i = args.index("moves")
            base, coups = args[:i], args[i + 1:]
        else:
            base, coups = args, []

        if base[:1] == ["startpos"]:
            board = chess.Board()
        elif base[:1] == ["fen"]:
            try:
                board = chess.Board(" ".join(base[1:]))
            except ValueError:
                return
        else:
            return

        for texte in coups:
            try:
                board.push_uci(texte)
            except ValueError:
                return  # coup illégal : on garde l'ancienne position
        self.board = board

    # ------------------------------------------------------------------
    # go [depth N] [movetime ms] [wtime ms btime ms winc ms binc ms] [infinite]
    # ------------------------------------------------------------------
    def go(self, args):
        params = {}
        i = 0
        while i < len(args):
            if args[i] == "infinite":
                params["infinite"] = 1
                i += 1
            elif i + 1 < len(args) and args[i + 1].lstrip("-").isdigit():
                params[args[i]] = int(args[i + 1])
                i += 2
            else:
                i += 1

        coup = self.chercher(self.board.copy(), params)
        self.envoyer(f"bestmove {coup.uci()}" if coup else "bestmove 0000")

    @staticmethod
    def budget_temps(board, params):
        """Temps (s) qu'on s'autorise pour ce coup, ou None si illimité."""
        if "movetime" in params:
            return params["movetime"] / 1000
        cle = "wtime" if board.turn == chess.WHITE else "btime"
        if cle in params:
            inc = params.get("winc" if board.turn == chess.WHITE else "binc", 0)
            return max(0.01, (params[cle] / 30 + inc / 2) / 1000)
        return None

    def chercher(self, board, params):
        """Approfondissement itératif : on garde le meilleur coup de la dernière
        profondeur terminée. Sans limite de temps, profondeur fixe."""
        budget = self.budget_temps(board, params)
        if budget is None:
            profondeur_max = params.get("depth", PROFONDEUR_DEFAUT)
        else:
            profondeur_max = params.get("depth", PROFONDEUR_MAX)

        debut = time.perf_counter()
        # Marge de sécurité : le temps de communication avec l'interface compte aussi.
        self.engine.echeance = None if budget is None else debut + max(0.005, budget * 0.8 - 0.02)
        meilleur = None
        for profondeur in range(1, profondeur_max + 1):
            t0 = time.perf_counter()
            try:
                coup, score = self.engine.chercher(board.copy(), profondeur)
            except TempsEcoule:
                break 
            if coup is None:
                break
            meilleur = coup
            ecoule = time.perf_counter() - debut
            self.envoyer(
                f"info depth {profondeur} score {self.format_score(score, board)} "
                f"nodes {self.engine.noeuds} time {int(ecoule * 1000)} "
                f"nps {int(self.engine.noeuds / max(time.perf_counter() - t0, 1e-9))} "
                f"pv {coup.uci()}"
            )
            if abs(score) >= MATE_SCORE - PROFONDEUR_MAX:
                break  # mat trouvé, inutile d'aller plus loin
            # La profondeur suivante coûte ~4-8x plus cher : inutile de la lancer
            # s'il ne reste pas de quoi la finir.
            if budget is not None and ecoule * 6 > budget:
                break
        self.engine.echeance = None
        if meilleur is None:  # aucune profondeur terminée : n'importe quel coup légal
            meilleur = next(iter(board.legal_moves), None)
        return meilleur

    @staticmethod
    def format_score(score, board):
        """Score UCI du point de vue du camp au trait (cp ou mate)."""
        if abs(score) >= MATE_SCORE - PROFONDEUR_MAX:
            plies = MATE_SCORE - abs(score)
            n = (plies + 1) // 2
            gagnant_trait = (score > 0) == (board.turn == chess.WHITE)
            return f"mate {n if gagnant_trait else -n}"
        cp = score if board.turn == chess.WHITE else -score
        return f"cp {int(cp)}"


def main():
    UCI().run()
