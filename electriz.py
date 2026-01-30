import chess
import random
import chess.svg
from IPython.display import SVG

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
        coup = choisir_coup_simple(board)

        print(coup)
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(board.fullmove_number)

    print(board.unicode())
if __name__ == "__main__":
    jouer_partie()
