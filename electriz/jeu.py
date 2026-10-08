"""Parties en console : IA contre IA, ou humain contre IA. Lancement : python -m electriz"""

import os
import random
from datetime import datetime

import chess
import chess.pgn
import chess.svg

from electriz.engine import Engine

DOSSIER_PARTIES = "data/raw/parties"
FICHIER_SVG = "echiquier.svg"
NIVEAUX = {
    1: "coup aléatoire",
    2: "capture si possible",
    3: "meilleur coup à 1 demi-coup",
    4: "alpha-bêta profondeur 3",
    5: "alpha-bêta profondeur 4",
}


def sauvegarder_partie_pgn(board, blancs="Electriz", noirs="Electriz", nom_fichier=None):
    """Sauvegarde la partie en PGN (importable sur Lichess/Chess.com)."""
    os.makedirs(DOSSIER_PARTIES, exist_ok=True)
    if nom_fichier is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nom_fichier = os.path.join(DOSSIER_PARTIES, f"partie_electriz_{timestamp}.pgn")

    game = chess.pgn.Game.from_board(board)
    game.headers["Event"] = "Electriz Development"
    game.headers["Site"] = "Local"
    game.headers["Date"] = datetime.now().strftime("%Y.%m.%d")
    game.headers["Round"] = "1"
    game.headers["White"] = blancs
    game.headers["Black"] = noirs
    game.headers["Result"] = board.result(claim_draw=True)

    with open(nom_fichier, "w", encoding="utf-8") as f:
        print(game, file=f, end="\n\n")
    print(f"Partie sauvegardée : {nom_fichier}")


def choisir_coup_aleatoire(board):
    return random.choice(list(board.legal_moves))


def choisir_coup_simple(board):
    coups_legaux = list(board.legal_moves)
    captures = [coup for coup in coups_legaux if board.is_capture(coup)]
    return random.choice(captures or coups_legaux)


def jouer_tour_ia(board, level, engine):
    match level:
        case 1:
            return choisir_coup_aleatoire(board)
        case 2:
            return choisir_coup_simple(board)
        case 3:
            return engine.choisir_coup_avec_evaluation(board)
        case 4:
            return engine.choisir_coup_minimax(board, profondeur=3)
        case 5:
            return engine.choisir_coup_minimax(board, profondeur=4)
        case _:
            raise ValueError(f"Niveau IA invalide : {level}")


def afficher_resultat(board):
    print(f"\nRésultat : {board.result(claim_draw=True)}")
    print(board.outcome(claim_draw=True))
    print(f"Nombre de coups complets : {board.fullmove_number}")


def jouer_partie(level=4):
    """IA contre IA."""
    board = chess.Board()
    engine = Engine()

    # claim_draw=True : on arrête aussi sur triple répétition / règle des 50 coups,
    # sinon deux IA déterministes peuvent tourner en rond très longtemps.
    while not board.is_game_over(claim_draw=True):
        coup = jouer_tour_ia(board, level, engine)
        print(f"{board.fullmove_number}{'.' if board.turn else '...'} {board.san(coup)}")
        board.push(coup)

    afficher_resultat(board)
    nom = f"Electriz niveau {level}"
    sauvegarder_partie_pgn(board, blancs=nom, noirs=nom)


def demander_coup_humain(board):
    while True:
        print("Coups légaux :", " ".join(board.san(m) for m in board.legal_moves))
        saisie = input("Votre coup (SAN, ex : e4, Nf3) : ").strip()
        try:
            return board.parse_san(saisie)  # lève une ValueError si illégal ou invalide
        except ValueError:
            print("Coup invalide ou illégal.")


def jouer_partie_human(level=4, color=chess.WHITE):
    """Humain contre IA. L'échiquier est redessiné dans echiquier.svg à chaque tour."""
    board = chess.Board()
    engine = Engine()

    while not board.is_game_over(claim_draw=True):
        dernier = board.peek() if board.move_stack else None
        with open(FICHIER_SVG, "w", encoding="utf-8") as f:
            f.write(chess.svg.board(board, orientation=color, lastmove=dernier))

        if board.turn == color:
            coup = demander_coup_humain(board)
            print(f"Vous jouez : {board.san(coup)}")  # SAN calculé AVANT push
        else:
            coup = jouer_tour_ia(board, level, engine)
            print(f"\nOrdinateur joue : {board.san(coup)}")
        board.push(coup)

    afficher_resultat(board)
    ia = f"Electriz niveau {level}"
    if color == chess.WHITE:
        sauvegarder_partie_pgn(board, blancs="Humain", noirs=ia)
    else:
        sauvegarder_partie_pgn(board, blancs=ia, noirs="Humain")


def demander_entier(question, choix, defaut):
    while True:
        saisie = input(f"{question} [{defaut}] : ").strip() or str(defaut)
        if saisie.isdigit() and int(saisie) in choix:
            return int(saisie)
        print(f"Choix possibles : {', '.join(map(str, choix))}")


def main():
    mode = demander_entier("Mode (1=IA vs IA, 2=Humain vs IA)", (1, 2), 1)
    for n, desc in NIVEAUX.items():
        print(f"  {n} : {desc}")
    level = demander_entier("Niveau IA", tuple(NIVEAUX), 4)

    if mode == 2:
        couleur = demander_entier("Couleur (1=blancs, 2=noirs)", (1, 2), 1)
        jouer_partie_human(level, chess.WHITE if couleur == 1 else chess.BLACK)
    else:
        jouer_partie(level)


if __name__ == "__main__":
    main()
