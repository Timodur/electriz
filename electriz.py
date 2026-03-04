import chess
import chess.pgn
import random
import os
from datetime import datetime
from src.engine.evaluation import Engine

def creer_dossier_data():
    """Crée le dossier data/raw/parties s'il n'existe pas"""
    os.makedirs("data/raw/parties", exist_ok=True)

def sauvegarder_partie_pgn(board, nom_fichier=None):
    """
    Sauvegarde la partie en PGN pour Lichess/Chess.com
    """
    creer_dossier_data()
    if nom_fichier is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = f"data/raw/parties/partie_electriz_{timestamp}.pgn"
    
    game = chess.pgn.Game.from_board(board)
    game.headers["Event"] = "Electriz Development"
    game.headers["Site"] = "Local"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "1"
    game.headers["White"] = "Electriz"
    game.headers["Black"] = "Electriz"
    game.headers["Result"] = board.result()
    
    with open(nom_fichier, "w", encoding="utf-8") as f:
        print(game, file=f, end="\n\n")
    print(f"Partie sauvegardée : {nom_fichier}")

def choisir_coup_aleatoire(board):
    """Niveau 1 : Coup aléatoire"""
    return random.choice(list(board.legal_moves))

def choisir_coup_simple(board):
    """Niveau 2 : Préfère les captures"""
    coups_legaux = list(board.legal_moves)
    captures = [coup for coup in coups_legaux if board.is_capture(coup)]
    return random.choice(captures) if captures else random.choice(coups_legaux)

def jouer_tour_ia(board, level):
    """Choisit le coup IA selon le niveau (fonction réutilisable)"""
    engine = Engine()
    match level:
        case 1:
            return choisir_coup_aleatoire(board)
        case 2:
            return choisir_coup_simple(board)
        case 3:
            return engine.choisir_coup_avec_evaluation(board)
        case 4:
            return engine.choisir_coup_minimax(board, profondeur=3)
        case _:
            raise ValueError(f"Niveau IA invalide : {level}")

def jouer_partie(level=4):
    """IA vs IA"""
    board = chess.Board()
    
    while not board.is_game_over():
        coup = jouer_tour_ia(board, level)
        print(f"IA (niveau {level}) joue : {coup}")
        board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    print(f"Nombre de coups complets : {board.fullmove_number}")
    sauvegarder_partie_pgn(board)

def jouer_partie_human(level=4):
    """Humain (blanc) vs IA (noir)"""
    board = chess.Board()
    
    while not board.is_game_over():
        # SVG avant chaque tour
        svg_data = chess.svg.board(board=board)
        with open("echiquier.svg", "w", encoding="utf-8") as f:
            f.write(svg_data)
        
        if board.turn == chess.WHITE:
            # Tour humain
            while True:
                legal_moves = [board.san(m) for m in board.legal_moves]
                print("Coups légaux :", legal_moves)
                user_input = input("Votre coup (SAN) : ")
                try:
                    coup = board.parse_san(user_input)
                    if coup in board.legal_moves:
                        board.push(coup)
                        print(f"Vous jouez : {board.san(coup)}")
                        break
                    else:
                        print("Coup non légal.")
                except ValueError:
                    print("Format SAN invalide (ex: e4, Nf3).")
        else:
            # Tour IA
            coup = jouer_tour_ia(board, level)
            print(f"\nOrdinateur joue : {board.san(coup)}")
            board.push(coup)
    
    print(f"\nRésultat : {board.result()}")
    print(board.outcome())
    sauvegarder_partie_pgn(board)

if __name__ == "__main__":
    mode = input("Mode (1=IA vs IA, 2=Humain vs IA) [1] : ").strip() or "1"
    level = int(input("Niveau IA (1-4) [4] : ").strip() or "4")
    
    if mode == "2":
        jouer_partie_human(level)
    else:
        jouer_partie(level)
