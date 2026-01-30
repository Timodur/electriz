import chess
import random

def choisir_coup_aleatoire(board):
    """Choisit un coup aléatoire parmi les coups légaux"""
    coups_legaux = list(board.legal_moves)
    return random.choice(coups_legaux)

def jouer_partie():
    board = chess.Board()
    
    while not board.is_game_over():
        print(f"\n{board}\n")
        
        coup = choisir_coup_aleatoire(board)
        print(f"Coup joué : {coup}")
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")

if __name__ == "__main__":
    jouer_partie()
