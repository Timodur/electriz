import chess
import chess.pgn
import glob
import os
import zstandard as zstd


def extract_positions(game):
    """Extrait les positions d'une partie."""
    positions = []
    board = game.board()
    for move in game.mainline_moves():
        board.push(move)
        positions.append(board.fen())
    return positions


def open_pgn_file(file_path):
    """Ouvre un fichier PGN, qu'il soit compressé (.zst) ou non."""
    if file_path.endswith('.zst'):
        return zstd.open(file_path, "rt", encoding="utf-8")
    else:
        return open(file_path, "r", encoding="utf-8")


def parse_pgn_file(file_path):
    """Parse un fichier PGN et extrait toutes les positions."""
    positions = []
    games_count = 0
    
    with open_pgn_file(file_path) as f:
        while game := chess.pgn.read_game(f):
            games_count += 1
            positions.extend(extract_positions(game))
            
            # Afficher la progression tous les 1000 parties
            if games_count % 1000 == 0:
                print(f"Traité {games_count} parties, {len(positions)} positions extraites")
    
    print(f"Terminé: {games_count} parties, {len(positions)} positions totales")
    return positions


# Exemple d'utilisation
if __name__ == "__main__":
    # Fonctionne avec les deux formats
    positions = parse_pgn_file("data/raw/Hikaru_all.pgn")
    positions = parse_pgn_file("data/raw/lichess_db_standard_rated_2025-12.pgn.zst")


