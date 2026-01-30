import chess
import random
import chess.svg
from IPython.display import SVG


def choisir_coup_aleatoire(board):
    """Choisit un coup aléatoire parmi les coups légaux"""
    coups_legaux = list(board.legal_moves)
    return random.choice(coups_legaux)

def jouer_partie():
    board = chess.Board()
    
    while not board.is_game_over():
        
        coup = choisir_coup_aleatoire(board)
        print(coup)
        SVG(chess.svg.board(board=board, lastmove=coup))
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(f"\nFEN finale : {board.fen()}")
    SVG(chess.svg.board(board=board, size=400))
if __name__ == "__main__":
    jouer_partie()
