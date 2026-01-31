import chess
import random
import chess.svg
from IPython.display import SVG
VALEURS_PIECES = {
    chess.PAWN: 1,
    chess.KNIGHT: 3,
    chess.BISHOP: 3,
    chess.ROOK: 5,
    chess.QUEEN: 9,
    chess.KING: 0
}
def evaluer_position(board):

    score = 0
    for piece_type in VALEURS_PIECES:
        pieces_blanches = len(board.pieces(piece_type, chess.WHITE))
        pieces_noires = len(board.pieces(piece_type, chess.BLACK))
        score += VALEURS_PIECES[piece_type] * pieces_blanches - VALEURS_PIECES[piece_type] * pieces_noires
    return score

def choisir_coup_avec_evaluation(board):
    coups_legaux = list(board.legal_moves)
    meilleur_score = -float('inf')
    meilleur_coup = None

    for coup in coups_legaux:
        board.push(coup)
        score = evaluer_position(board)
        board.pop()
        if score > meilleur_score:
            meilleur_score = score
            meilleur_coup = coup
    return meilleur_coup

def choisir_coup_simple(board):
    coups_legaux = list(board.legal_moves)
    capture = []
    for coup in coups_legaux:
        if board.is_capture(coup):
            capture.append(coup)
    if capture:
        return random.choice(capture)
    return random.choice(coups_legaux)

def choisir_coup_aleatoire(board):
    """Choisit un coup aléatoire parmi les coups légaux"""
    coups_legaux = list(board.legal_moves)
    return random.choice(coups_legaux)

def jouer_partie():
    board = chess.Board()
    
    while not board.is_game_over():
        #coup = choisir_coup_aleatoire(board)       #level 1
        #coup = choisir_coup_simple(board)          #level 2
        coup = choisir_coup_avec_evaluation(board)  #level 3 
        

        print(coup)
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(board.fullmove_number)

    print(board.unicode())
if __name__ == "__main__":
    jouer_partie()
