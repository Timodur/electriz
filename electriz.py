import chess
import random
import chess.svg
import time
from IPython.display import SVG
from src.engine.evaluation import Engine

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
        time.sleep(1)
        #coup = choisir_coup_aleatoire(board)       #level 1
        #coup = choisir_coup_simple(board)          #level 2
        engine = Engine()
        coup = engine.choisir_coup_avec_evaluation(board)  #level 3 
        

        print(coup)
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(board.fullmove_number)

    svg_data = chess.svg.board(board=board)
    with open("echiquier.svg", "w", encoding="utf-8") as f:
        f.write(svg_data)
if __name__ == "__main__":
    jouer_partie()
