from turtle import color
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
    CENTER_BONUS = {
        # Bonus selon la distance au centre (e4, d4, e5, d5)
        chess.E4: 30, chess.D4: 30, chess.E5: 30, chess.D5: 30,  # Centre parfait
        chess.C4: 20, chess.C5: 20, chess.D3: 20, chess.E3: 20,  # Centre étendu
        chess.F4: 20, chess.F5: 20, chess.D6: 20, chess.E6: 20,
        chess.C3: 10, chess.C6: 10, chess.F3: 10, chess.F6: 10   # Proche du centre
    }
    def evaluer_position(self, board):
        if board.is_checkmate():
            return -float('inf') if board.turn == chess.WHITE else float('inf')
        
        if board.is_stalemate() or board.is_insufficient_material() or board.can_claim_fifty_moves() or board.can_claim_threefold_repetition():
            return 0
        
        score = 0

        score += self.evaluate_material_balance(board)

        score += self.evaluate_mobility(board)

        score += self.evaluate_center_control(board)

        score += self.evaluate_development(board)

        score += self.evaluate_attacked_pieces(board)

        score += self.evaluate_king_safety(board)

                
        return score
    def evaluate_material_balance(self, board):
        score = 0
        for piece_type in self.VALEURS_PIECES:
            pieces_blanches = len(board.pieces(piece_type, chess.WHITE))
            pieces_noires = len(board.pieces(piece_type, chess.BLACK))
            score += self.VALEURS_PIECES[piece_type] * pieces_blanches - self.VALEURS_PIECES[piece_type] * pieces_noires
        return score
    
    def evaluate_mobility(self, board):
        mobilite = board.legal_moves.count()
        score = mobilite * 10 if board.turn == chess.WHITE else -mobilite * 10
        return score
    
    def evaluate_center_control(self, board):
        white_center = 0
        black_center = 0
        for square in self.CENTER_BONUS:
            if board.piece_at(square) and board.color_at(square) == chess.WHITE:
                white_center += self.CENTER_BONUS[square]
            if board.piece_at(square) and board.color_at(square) == chess.BLACK:
                black_center += self.CENTER_BONUS[square]

        return white_center - black_center
    def evaluate_development(self, board):

        initial_positions = {
            chess.WHITE: {
                chess.BISHOP: {chess.C1, chess.F1},
                chess.KNIGHT: {chess.B1, chess.G1}
            },
            chess.BLACK: {
                chess.BISHOP: {chess.C8, chess.F8},
                chess.KNIGHT: {chess.B8, chess.G8}
            }
        }
        
        def count_undeveloped(color):
            return sum(
                len(board.pieces(piece_type, color) & initial_squares)
                for piece_type, initial_squares in initial_positions[color].items()
            )
        
        # Pénalité pour les pièces non développées
        white_undeveloped = count_undeveloped(chess.WHITE)
        black_undeveloped = count_undeveloped(chess.BLACK)
        
        return (black_undeveloped - white_undeveloped) * 20
    
    def evaluate_attacked_pieces(self, board):

        score = 0
        
        # Parcourir toutes les pièces (sauf le roi)
        for piece_type, valeur in self.VALEURS_PIECES.items():
            if piece_type == chess.KING:
                continue  
            
            penalite_base = valeur * 0.3
            

            for color, sign in [(chess.WHITE, -1), (chess.BLACK, 1)]:
                opponent = not color
                
                for square in board.pieces(piece_type, color):
                    if board.is_attacked_by(opponent, square):
                        if board.is_attacked_by(color, square):
                            penalite = penalite_base
                        else:
                            penalite = penalite_base * 2
                        
                        score += sign * penalite
        
        return score
    def evaluate_king_safety(self, board):
        white_safety = 0
        black_safety = 0
        
        # Vérifier la position du roi blanc
        white_king_square = board.king(chess.WHITE)
        if white_king_square:
            col = chess.square_file(white_king_square)
            if col in [0, 1, 6, 7]:
                white_safety += 50
            elif col in [3, 4]:
                white_safety -= 40
        
        # Vérifier la position du roi noir
        black_king_square = board.king(chess.BLACK)
        if black_king_square:
            case = chess.square_file(black_king_square)
            if case in [0, 1, 6, 7]:
                black_safety += 50
            elif case in [3, 4]:
                black_safety -= 40
        
        return white_safety - black_safety
        
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
        print(f"Évaluation du coup {evaluation/100:.2f} ")

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


        
        
        