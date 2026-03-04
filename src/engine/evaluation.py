import chess
import random

class Engine:
    VALEURS_PIECES = {
        chess.PAWN:   100,
        chess.KNIGHT: 300,
        chess.BISHOP: 300,
        chess.ROOK:   500,
        chess.QUEEN:  900,
        chess.KING:   200000
    }
    # TODO : improve table -> https://www.chessprogramming.org/PeSTO%27s_Evaluation_Function
    _PAWN_TABLE = [
         0,   0,   0,   0,   0,   0,   0,   0,
         5,  10,  10, -20, -20,  10,  10,   5,
         5,  -5, -10,   0,   0, -10,  -5,   5,
         0,   0,   0,  20,  20,   0,   0,   0,
         5,   5,  10,  25,  25,  10,   5,   5,
        10,  10,  20,  30,  30,  20,  10,  10,
        50,  50,  50,  50,  50,  50,  50,  50,
         0,   0,   0,   0,   0,   0,   0,   0,
    ]
    _KNIGHT_TABLE = [
       -50, -40, -30, -30, -30, -30, -40, -50,
       -40, -20,   0,   5,   5,   0, -20, -40,
       -30,   5,  10,  15,  15,  10,   5, -30,
       -30,   0,  15,  20,  20,  15,   0, -30,
       -30,   5,  15,  20,  20,  15,   5, -30,
       -30,   0,  10,  15,  15,  10,   0, -30,
       -40, -20,   0,   0,   0,   0, -20, -40,
       -50, -40, -30, -30, -30, -30, -40, -50,
    ]
    _BISHOP_TABLE = [
       -20, -10, -10, -10, -10, -10, -10, -20,
       -10,   5,   0,   0,   0,   0,   5, -10,
       -10,  10,  10,  10,  10,  10,  10, -10,
       -10,   0,  10,  10,  10,  10,   0, -10,
       -10,   5,   5,  10,  10,   5,   5, -10,
       -10,   0,   5,  10,  10,   5,   0, -10,
       -10,   0,   0,   0,   0,   0,   0, -10,
       -20, -10, -10, -10, -10, -10, -10, -20,
    ]
    _ROOK_TABLE = [
         0,   0,   0,   5,   5,   0,   0,   0,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
        -5,   0,   0,   0,   0,   0,   0,  -5,
         5,  10,  10,  10,  10,  10,  10,   5,
         0,   0,   0,   0,   0,   0,   0,   0,
    ]
    _QUEEN_TABLE = [
       -20, -10, -10,  -5,  -5, -10, -10, -20,
       -10,   0,   5,   0,   0,   0,   0, -10,
       -10,   5,   5,   5,   5,   5,   0, -10,
         0,   0,   5,   5,   5,   5,   0,  -5,
        -5,   0,   5,   5,   5,   5,   0,  -5,
       -10,   0,   5,   5,   5,   5,   0, -10,
       -10,   0,   0,   0,   0,   0,   0, -10,
       -20, -10, -10,  -5,  -5, -10, -10, -20,
    ]
    _KING_MIDDLEGAME_TABLE = [
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -30, -40, -40, -50, -50, -40, -40, -30,
        -20, -30, -30, -40, -40, -30, -30, -20,
        -10, -20, -20, -20, -20, -20, -20, -10,
         20,  20,   0,   0,   0,   0,  20,  20,
         20,  30,  10,   0,   0,  10,  30,  20
    ]
    _KING_ENDGAME_TABLE = [
        -50, -40, -30, -20, -20, -30, -40, -50,
        -30, -20, -10,   0,   0, -10, -20, -30,
        -30, -10,  20,  30,  30,  20, -10, -30,
        -30, -10,  30,  40,  40,  30, -10, -30,
        -30, -10,  30,  40,  40,  30, -10, -30,
        -30, -10,  20,  30,  30,  20, -10, -30,
        -30, -30,   0,   0,   0,   0, -30, -30,
        -50, -30, -30, -30, -30, -30, -30, -50
    ]
    #TODO : king safety (short)-> https://www.chessprogramming.org/King_Safety#PawnShield
    #TODO : pawn structure (long) -> https://www.chessprogramming.org/Pawn_Structure
    #TODO : and more... (long) -> https://www.chessprogramming.org/Evaluation
    @staticmethod
    def _mirror(table):
        return sum([table[i:i+8] for i in range(0, 64, 8)][::-1], [])

    @staticmethod
    def _make_bonus(table):
        return dict(zip(chess.SQUARES, table))

    def __init__(self):
        self.WHITE_PAWN_BONUS   = self._make_bonus(self._PAWN_TABLE)
        self.WHITE_KNIGHT_BONUS = self._make_bonus(self._KNIGHT_TABLE)
        self.WHITE_BISHOP_BONUS = self._make_bonus(self._BISHOP_TABLE)
        self.WHITE_ROOK_BONUS   = self._make_bonus(self._ROOK_TABLE)
        self.WHITE_QUEEN_BONUS  = self._make_bonus(self._QUEEN_TABLE)
        self.WHITE_KING_BONUS   = self._make_bonus(self._KING_MIDDLEGAME_TABLE)

        self.BLACK_PAWN_BONUS   = self._make_bonus(self._mirror(self._PAWN_TABLE))
        self.BLACK_KNIGHT_BONUS = self._make_bonus(self._mirror(self._KNIGHT_TABLE))
        self.BLACK_BISHOP_BONUS = self._make_bonus(self._mirror(self._BISHOP_TABLE))
        self.BLACK_ROOK_BONUS   = self._make_bonus(self._mirror(self._ROOK_TABLE))
        self.BLACK_QUEEN_BONUS  = self._make_bonus(self._mirror(self._QUEEN_TABLE))
        self.BLACK_KING_BONUS   = self._make_bonus(self._mirror(self._KING_MIDDLEGAME_TABLE))
        
        self.WHITE_PIECE_BONUS = {
            chess.PAWN: self.WHITE_PAWN_BONUS,
            chess.KNIGHT: self.WHITE_KNIGHT_BONUS,
            chess.BISHOP: self.WHITE_BISHOP_BONUS,
            chess.ROOK: self.WHITE_ROOK_BONUS,
            chess.QUEEN: self.WHITE_QUEEN_BONUS,
            chess.KING: self.WHITE_KING_BONUS,
        }
        
        self.BLACK_PIECE_BONUS = {
            chess.PAWN: self.BLACK_PAWN_BONUS,
            chess.KNIGHT: self.BLACK_KNIGHT_BONUS,
            chess.BISHOP: self.BLACK_BISHOP_BONUS,
            chess.ROOK: self.BLACK_ROOK_BONUS,
            chess.QUEEN: self.BLACK_QUEEN_BONUS,
            chess.KING: self.BLACK_KING_BONUS,
        }
    
    def evaluer_position(self, board):
        score = 0

        score += self.evaluate_material_balance(board)

        score += self.evaluate_piece_position(board)
        return score
    def evaluate_material_balance(self, board):
        score = 0
        for piece_type in self.VALEURS_PIECES:
            pieces_blanches = len(board.pieces(piece_type, chess.WHITE))
            pieces_noires = len(board.pieces(piece_type, chess.BLACK))
            score += self.VALEURS_PIECES[piece_type] * pieces_blanches - self.VALEURS_PIECES[piece_type] * pieces_noires
        return score
    
    def evaluate_piece_position(self, board):
        score = 0
        for piece_type in self.VALEURS_PIECES:
            for square in board.pieces(piece_type, chess.WHITE):
                score += self.WHITE_PIECE_BONUS[piece_type][square]
            for square in board.pieces(piece_type, chess.BLACK):
                score -= self.BLACK_PIECE_BONUS[piece_type][square]
        return score
    
    def evaluate_mobility(self, board):
        #TODO : improve mobility evaluation
        mobilite = board.legal_moves.count()
        score = mobilite * 10 if board.turn == chess.WHITE else -mobilite * 10
        return score
    

    
    
    def evaluate_king_safety(self, board):
        # TODO : implement king safety evaluation
        return 0
        
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
        
        print(f"Évaluation du coup {meilleure_eval/100:.2f} ")    
        return meilleur_coup
    def choisir_coup_minimax(self, board, profondeur=3):
        coups_legaux = list(board.legal_moves)
        
        if not coups_legaux:
            return None
        
        # Initialise selon qui joue
        meilleure_eval = float('-inf') if board.turn == chess.WHITE else float('inf')
        meilleur_coup = coups_legaux[0]
        couleur_initiale = board.turn 
        
        for coup1 in coups_legaux:
            board.push(coup1)
            
            # Évalue la position après coup1 avec minimax profondeur 2
            evaluation = self.minimax(board, profondeur - 1)
            board.pop()
            
            # Maximise pour blancs, minimise pour noirs
            if couleur_initiale == chess.WHITE:
                if evaluation > meilleure_eval:
                    meilleure_eval = evaluation
                    meilleur_coup = coup1
            else:
                if evaluation < meilleure_eval:
                    meilleure_eval = evaluation
                    meilleur_coup = coup1

        return meilleur_coup

    def minimax(self, board, profondeur):
        if profondeur == 0 or board.is_game_over():
            
            return self.evaluer_position(board)
        
        coups_legaux = list(board.legal_moves)
        
        # Maximise pour les blancs
        if board.turn == chess.WHITE:
            max_eval = float('-inf')
            for coup in coups_legaux:
                board.push(coup)
                evaluation = self.minimax(board, profondeur - 1)
                board.pop()
                max_eval = max(max_eval, evaluation)
            return max_eval
        
        # Minimise pour les noirs
        else:
            min_eval = float('inf')
            for coup in coups_legaux:
                board.push(coup)
                evaluation = self.minimax(board, profondeur - 1)
                board.pop()
                min_eval = min(min_eval, evaluation)
            return min_eval


        
        
        