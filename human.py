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
    coups_legaux = list(board.legal_moves)
    return random.choice(coups_legaux)

def jouer_partie():
    board = chess.Board()
    
    while not board.is_game_over():
        svg_data = chess.svg.board(board=board)
        with open("echiquier.svg", "w", encoding="utf-8") as f:
            f.write(svg_data)
        if board.turn == chess.WHITE:
        # Tour du joueur
            while True:
                print("coup légal(s) :", [str(m) for m in board.legal_moves])
                user_input = input("Votre coup : ")

                    
                if (coup:= chess.Move.from_uci(user_input)) in board.legal_moves:
                    board.push(coup)
                    break
        else:
            # Tour de l'ordinateur
            #coup = choisir_coup_aleatoire(board)      #level 1
            coup = choisir_coup_simple(board)         #level 2

            print(f"\nOrdinateur joue : {coup}")
            board.push(coup)
        
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(board.fullmove_number)

    svg_data = chess.svg.board(board=board)
    with open("echiquier.svg", "w", encoding="utf-8") as f:
        f.write(svg_data)
if __name__ == "__main__":
    jouer_partie()