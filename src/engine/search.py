"""Recherche du meilleur coup : minimax et élagage alpha-bêta.

Sources :
- Minimax : https://fr.wikipedia.org/wiki/Algorithme_minimax
- Élagage alpha-bêta : https://fr.wikipedia.org/wiki/%C3%89lagage_alpha-b%C3%AAta
- MVV-LVA : https://www.chessprogramming.org/MVV-LVA

Les Blancs maximisent le score, les Noirs le minimisent.
"""

import chess

from .evaluation import Evaluation

# Score d'un mat. On retire la distance (en demi-coups) pour préférer le mat
# le plus rapide et retarder le plus possible un mat subi.
MATE_SCORE = 100_000
INFINI = float("inf")


class Engine(Evaluation):
    def __init__(self):
        self.noeuds = 0  # positions visitées lors de la dernière recherche

    # ------------------------------------------------------------------
    # Positions terminales
    # ------------------------------------------------------------------
    @staticmethod
    def _score_terminal(board, ply):
        """Score si la partie est finie (mat ou nulle), sinon None."""
        outcome = board.outcome()
        if outcome is None:
            return None
        if outcome.winner is None:
            return 0  # pat, matériel insuffisant, 75 coups, 5 répétitions
        # Le camp au trait est maté.
        return MATE_SCORE - ply if outcome.winner == chess.WHITE else -(MATE_SCORE - ply)

    # ------------------------------------------------------------------
    # Tri des coups (améliore beaucoup l'élagage alpha-bêta)
    # ------------------------------------------------------------------
    def _ordonner_coups(self, board):
        def priorite(coup):
            p = 0
            if coup.promotion:
                p += 10 * self.VALEURS_PIECES[coup.promotion]
            if board.is_capture(coup):
                # MVV-LVA : plus grosse victime d'abord, plus petit attaquant d'abord.
                victime = board.piece_type_at(coup.to_square) or chess.PAWN  # en passant
                attaquant = board.piece_type_at(coup.from_square)
                p += 10 * self.VALEURS_PIECES[victime] - self.VALEURS_PIECES.get(attaquant, 0)
            return p

        return sorted(board.legal_moves, key=priorite, reverse=True)

    # ------------------------------------------------------------------
    # Recherche
    # ------------------------------------------------------------------
    def minimax(self, board, profondeur, ply=0):
        """Minimax sans élagage. Conservé comme référence pour les tests."""
        self.noeuds += 1
        terminal = self._score_terminal(board, ply)
        if terminal is not None:
            return terminal
        if profondeur == 0:
            return self.evaluer_position(board)

        maximiser = board.turn == chess.WHITE
        meilleur = -INFINI if maximiser else INFINI
        for coup in board.legal_moves:
            board.push(coup)
            valeur = self.minimax(board, profondeur - 1, ply + 1)
            board.pop()
            meilleur = max(meilleur, valeur) if maximiser else min(meilleur, valeur)
        return meilleur

    def alphabeta(self, board, profondeur, alpha=-INFINI, beta=INFINI, ply=0):
        """Minimax avec élagage alpha-bêta : même résultat, beaucoup moins de nœuds."""
        self.noeuds += 1
        terminal = self._score_terminal(board, ply)
        if terminal is not None:
            return terminal
        if profondeur == 0:
            return self.evaluer_position(board)

        if board.turn == chess.WHITE:
            meilleur = -INFINI
            for coup in self._ordonner_coups(board):
                board.push(coup)
                meilleur = max(meilleur, self.alphabeta(board, profondeur - 1, alpha, beta, ply + 1))
                board.pop()
                alpha = max(alpha, meilleur)
                if alpha >= beta:
                    break  # coupure bêta : les Noirs n'autoriseront pas cette ligne
            return meilleur
        else:
            meilleur = INFINI
            for coup in self._ordonner_coups(board):
                board.push(coup)
                meilleur = min(meilleur, self.alphabeta(board, profondeur - 1, alpha, beta, ply + 1))
                board.pop()
                beta = min(beta, meilleur)
                if alpha >= beta:
                    break  # coupure alpha : les Blancs n'autoriseront pas cette ligne
            return meilleur

    def chercher(self, board, profondeur=3):
        """Renvoie (meilleur_coup, score) avec alpha-bêta à la profondeur donnée.
        meilleur_coup vaut None si la partie est déjà finie."""
        self.noeuds = 0
        maximiser = board.turn == chess.WHITE
        alpha, beta = -INFINI, INFINI
        meilleur_coup, meilleur_score = None, (-INFINI if maximiser else INFINI)

        for coup in self._ordonner_coups(board):
            board.push(coup)
            score = self.alphabeta(board, profondeur - 1, alpha, beta, ply=1)
            board.pop()
            if maximiser and score > meilleur_score:
                meilleur_coup, meilleur_score = coup, score
                alpha = max(alpha, score)
            elif not maximiser and score < meilleur_score:
                meilleur_coup, meilleur_score = coup, score
                beta = min(beta, score)
        return meilleur_coup, meilleur_score

    # API utilisée par electriz.py (niveaux 3 et 4)
    def choisir_coup_avec_evaluation(self, board):
        """Niveau 3 : meilleur coup à 1 demi-coup (détecte les mats en 1)."""
        return self.chercher(board, profondeur=1)[0]

    def choisir_coup_minimax(self, board, profondeur=3):
        """Niveau 4 : alpha-bêta (même choix de valeur que minimax, plus rapide)."""
        return self.chercher(board, profondeur)[0]
