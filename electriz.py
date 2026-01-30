import chess
import random

def jouer_partie_aleatoire():
    board = chess.Board()
    numero_coup = 1
    
    while not board.is_game_over():
        print(f"\n{'='*50}")
        print(f"Coup n°{numero_coup}")
        print(board)
        print(f"\nTour des {'BLANCS' if board.turn else 'NOIRS'}")
        
        # Choisit un coup aléatoire
        coup = random.choice(list(board.legal_moves))
        print(f"Coup joué : {coup}")
        
        board.push(coup)
        numero_coup += 1
    
    print(f"\n{'='*50}")
    print("PARTIE TERMINÉE !")
    print(board)
    print(f"\nRésultat : {board.result()}")
    print(f"Raison : {board.outcome()}")

if __name__ == "__main__":
    jouer_partie_aleatoire()
