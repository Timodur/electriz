import chess
import random
import chess.svg
import time
import datetime
from datetime import datetime
from IPython.display import SVG
from src.engine.evaluation import Engine
def sauvegarder_partie_pgn(board, nom_fichier=None):
    """
    Sauvegarde la partie en PGN pour Lichess/Chess.com
    """
    if nom_fichier is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"partie_electriz_{timestamp}.pgn"
    
    # Crée le PGN
    game = chess.pgn.Game.from_board(board)
    
    # Métadonnées
    game.headers["Event"] = "Electriz Development"
    game.headers["Site"] = "Local"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "1"
    game.headers["White"] = "Electriz"
    game.headers["Black"] = "Electriz"
    game.headers["Result"] = board.result()
    
    # Sauvegarde
    with open(nom_fichier, "w", encoding="utf-8") as f:
        print(game, file=f, end="\n\n")
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
        #time.sleep(1)
        #coup = choisir_coup_aleatoire(board)       #level 1
        #coup = choisir_coup_simple(board)          #level 2
        engine = Engine()
        coup = engine.choisir_coup_minimax(board)  #level 4
        

        print(coup)
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(board.fullmove_number)

    nom_pgn = sauvegarder_partie_pgn(board)
if __name__ == "__main__":
    jouer_partie()
