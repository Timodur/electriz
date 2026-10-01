"""Évaluation statique d'une position (matériel + tables pièce-case).

Sources :
- Tables pièce-case : "Simplified Evaluation Function" (Tomasz Michniewski),
  https://www.chessprogramming.org/Simplified_Evaluation_Function

Convention : tous les scores sont en centipions, du point de vue des Blancs
(positif = avantage Blanc).
"""

import chess


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


class Evaluation:
    """Évaluation statique, héritée par le moteur de recherche (search.Engine)."""

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
