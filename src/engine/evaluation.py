"""Évaluation statique et recherche du moteur Electriz.

Sources :
- Tables pièce-case : "Simplified Evaluation Function" (Tomasz Michniewski),
  https://www.chessprogramming.org/Simplified_Evaluation_Function
- Minimax : https://fr.wikipedia.org/wiki/Algorithme_minimax
- Élagage alpha-bêta : https://fr.wikipedia.org/wiki/%C3%89lagage_alpha-b%C3%AAta
- MVV-LVA : https://www.chessprogramming.org/MVV-LVA

Convention : tous les scores sont en centipions, du point de vue des Blancs
(positif = avantage Blanc). Les Blancs maximisent, les Noirs minimisent.
"""

import chess

# Score d'un mat. On retire la distance (en demi-coups) pour préférer le mat
# le plus rapide et retarder le plus possible un mat subi.
MATE_SCORE = 100_000
INFINI = float("inf")


def _depuis_rang8(table):
    """Convertit une table écrite « visuellement » (rang 8 en haut, comme sur
    chessprogramming.org) vers l'indexation de python-chess (A1 = 0, H8 = 63)."""
    rangs = [table[i:i + 8] for i in range(0, 64, 8)]
    return [v for rang in reversed(rangs) for v in rang]


# Toutes les tables sont écrites du point de vue des Blancs, rang 8 en haut,
# exactement comme sur la page chessprogramming.org citée plus haut.
_PAWN_TABLE = _depuis_rang8([
     0,   0,   0,   0,   0,   0,   0,   0,
    50,  50,  50,  50,  50,  50,  50,  50,
    10,  10,  20,  30,  30,  20,  10,  10,
     5,   5,  10,  25,  25,  10,   5,   5,
     0,   0,   0,  20,  20,   0,   0,   0,
     5,  -5, -10,   0,   0, -10,  -5,   5,
     5,  10,  10, -20, -20,  10,  10,   5,
     0,   0,   0,   0,   0,   0,   0,   0,
])
_KNIGHT_TABLE = _depuis_rang8([
   -50, -40, -30, -30, -30, -30, -40, -50,
   -40, -20,   0,   0,   0,   0, -20, -40,
   -30,   0,  10,  15,  15,  10,   0, -30,
   -30,   5,  15,  20,  20,  15,   5, -30,
   -30,   0,  15,  20,  20,  15,   0, -30,
   -30,   5,  10,  15,  15,  10,   5, -30,
   -40, -20,   0,   5,   5,   0, -20, -40,
   -50, -40, -30, -30, -30, -30, -40, -50,
])
_BISHOP_TABLE = _depuis_rang8([
   -20, -10, -10, -10, -10, -10, -10, -20,
   -10,   0,   0,   0,   0,   0,   0, -10,
   -10,   0,   5,  10,  10,   5,   0, -10,
   -10,   5,   5,  10,  10,   5,   5, -10,
   -10,   0,  10,  10,  10,  10,   0, -10,
   -10,  10,  10,  10,  10,  10,  10, -10,
   -10,   5,   0,   0,   0,   0,   5, -10,
   -20, -10, -10, -10, -10, -10, -10, -20,
])
_ROOK_TABLE = _depuis_rang8([
     0,   0,   0,   0,   0,   0,   0,   0,
     5,  10,  10,  10,  10,  10,  10,   5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
    -5,   0,   0,   0,   0,   0,   0,  -5,
     0,   0,   0,   5,   5,   0,   0,   0,
])
_QUEEN_TABLE = _depuis_rang8([
   -20, -10, -10,  -5,  -5, -10, -10, -20,
   -10,   0,   0,   0,   0,   0,   0, -10,
   -10,   0,   5,   5,   5,   5,   0, -10,
    -5,   0,   5,   5,   5,   5,   0,  -5,
     0,   0,   5,   5,   5,   5,   0,  -5,
   -10,   5,   5,   5,   5,   5,   0, -10,
   -10,   0,   5,   0,   0,   0,   0, -10,
   -20, -10, -10,  -5,  -5, -10, -10, -20,
])
_KING_MIDDLEGAME_TABLE = _depuis_rang8([
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -30, -40, -40, -50, -50, -40, -40, -30,
   -20, -30, -30, -40, -40, -30, -30, -20,
   -10, -20, -20, -20, -20, -20, -20, -10,
    20,  20,   0,   0,   0,   0,  20,  20,
    20,  30,  10,   0,   0,  10,  30,  20,
])
_KING_ENDGAME_TABLE = _depuis_rang8([
   -50, -40, -30, -20, -20, -30, -40, -50,
   -30, -20, -10,   0,   0, -10, -20, -30,
   -30, -10,  20,  30,  30,  20, -10, -30,
   -30, -10,  30,  40,  40,  30, -10, -30,
   -30, -10,  30,  40,  40,  30, -10, -30,
   -30, -10,  20,  30,  30,  20, -10, -30,
   -30, -30,   0,   0,   0,   0, -30, -30,
   -50, -30, -30, -30, -30, -30, -30, -50,
])

# TODO : passer aux tables PeSTO (milieu/finale interpolés)
#        -> https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
# TODO : sécurité du roi (court) -> https://www.chessprogramming.org/King_Safety#PawnShield
# TODO : structure de pions (long) -> https://www.chessprogramming.org/Pawn_Structure
# TODO : et plus… (long) -> https://www.chessprogramming.org/Evaluation


class Engine:
    # Le roi n'a pas de valeur matérielle : il est toujours présent des deux
    # côtés (les coups légaux de python-chess ne permettent pas de le prendre).
    VALEURS_PIECES = {
        chess.PAWN: 100,
        chess.KNIGHT: 320,
        chess.BISHOP: 330,
        chess.ROOK: 500,
        chess.QUEEN: 900,
    }

    # Tables construites une seule fois pour toutes les instances.
    # Pour les Noirs on lit la case symétrique : chess.square_mirror(case).
    TABLES = {
        chess.PAWN: _PAWN_TABLE,
        chess.KNIGHT: _KNIGHT_TABLE,
        chess.BISHOP: _BISHOP_TABLE,
        chess.ROOK: _ROOK_TABLE,
        chess.QUEEN: _QUEEN_TABLE,
    }

    def __init__(self):
        self.noeuds = 0  # positions visitées lors de la dernière recherche

    # ------------------------------------------------------------------
    # Évaluation statique
    # ------------------------------------------------------------------
    def evaluer_position(self, board):
        """Score statique (matériel + position), du point de vue des Blancs."""
        return self.evaluate_material_balance(board) + self.evaluate_piece_position(board)

    def evaluate_material_balance(self, board):
        score = 0
        for piece_type, valeur in self.VALEURS_PIECES.items():
            score += valeur * (
                len(board.pieces(piece_type, chess.WHITE))
                - len(board.pieces(piece_type, chess.BLACK))
            )
        return score

    def evaluate_piece_position(self, board):
        table_roi = _KING_ENDGAME_TABLE if self.est_finale(board) else _KING_MIDDLEGAME_TABLE
        score = 0
        for square, piece in board.piece_map().items():
            table = table_roi if piece.piece_type == chess.KING else self.TABLES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += table[square]
            else:
                score -= table[chess.square_mirror(square)]
        return score

    @staticmethod
    def est_finale(board):
        """Critère de la Simplified Evaluation Function : finale si aucun camp
        n'a de dame, ou si chaque camp qui a une dame a au plus une pièce mineure
        en plus (et aucune tour)."""
        for couleur in (chess.WHITE, chess.BLACK):
            if not board.pieces(chess.QUEEN, couleur):
                continue
            mineures = len(board.pieces(chess.KNIGHT, couleur)) + len(board.pieces(chess.BISHOP, couleur))
            if board.pieces(chess.ROOK, couleur) or mineures > 1:
                return False
        return True

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
