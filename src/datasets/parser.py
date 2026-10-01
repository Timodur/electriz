"""Extraction des positions (FEN) depuis des fichiers PGN, compressés (.zst) ou non.

Les bases Lichess (https://database.lichess.org/) font des dizaines de Go :
on lit donc les parties une par une (générateur) au lieu de tout charger en mémoire.
"""

import argparse
import io
from itertools import islice

import chess.pgn
import zstandard as zstd


def extract_positions(game):
    """Renvoie les FEN de toutes les positions d'une partie (après chaque coup)."""
    positions = []
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        positions.append(board.fen())
    return positions


def open_pgn_file(file_path):
    """Ouvre un fichier PGN en texte, qu'il soit compressé (.zst) ou non."""
    if file_path.endswith(".zst"):
        flux = zstd.ZstdDecompressor().stream_reader(open(file_path, "rb"), closefd=True)
        return io.TextIOWrapper(flux, encoding="utf-8")
    return open(file_path, "r", encoding="utf-8")


def iter_games(file_path):
    """Générateur : lit les parties une à une."""
    with open_pgn_file(file_path) as f:
        while (game := chess.pgn.read_game(f)) is not None:
            yield game


def iter_positions(file_path, max_games=None):
    """Générateur : produit les FEN partie par partie, sans tout garder en mémoire."""
    for i, game in enumerate(islice(iter_games(file_path), max_games), start=1):
        yield from extract_positions(game)
        if i % 1000 == 0:
            print(f"{i} parties traitées")


def parse_pgn_file(file_path, max_games=None):
    """Renvoie la liste des positions. À réserver aux petits fichiers
    (ou utiliser max_games) : préférer iter_positions pour les grosses bases."""
    positions = list(iter_positions(file_path, max_games))
    print(f"Terminé : {len(positions)} positions")
    return positions


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pgn", help="fichier .pgn ou .pgn.zst, ex. data/raw/Hikaru_all.pgn")
    parser.add_argument("--max-games", type=int, default=1000)
    args = parser.parse_args()
    parse_pgn_file(args.pgn, args.max_games)
