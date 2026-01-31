import chess
import random

class Engine:
    VALEURS_PIECES = {
        chess.PAWN: 100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK: 500,
        chess.QUEEN: 900,
        chess.KING: 0
    }
    def evaluer_position(self, board):
        if board.is_checkmate():
            return -float('inf') if board.turn == chess.WHITE else float('inf')
        
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        
        score = 0
        for piece_type in self.VALEURS_PIECES:
            pieces_blanches = len(board.pieces(piece_type, chess.WHITE))
            pieces_noires = len(board.pieces(piece_type, chess.BLACK))
            score += self.VALEURS_PIECES[piece_type] * pieces_blanches - self.VALEURS_PIECES[piece_type] * pieces_noires
        return score

    def choisir_coup_avec_evaluation(self, board):
        coups_legaux = list(board.legal_moves)
        meilleure_eval = float('-inf') if board.turn == chess.WHITE else float('inf')
        meilleur_coup = None

        for coup in coups_legaux:
            board.push(coup)
            evaluation = self.evaluer_position(board)
            board.pop()
            if board.turn == chess.WHITE:
                if evaluation > meilleure_eval:
                    meilleure_eval = evaluation
                    meilleur_coup = coup
            else:
                if evaluation < meilleure_eval:
                    meilleure_eval = evaluation
                    meilleur_coup = coup
        
            
        return meilleur_coup