#Test de performance standard UCI pour mesurer vitesse moteur (nodes/sec)
"""Benchmark du moteur : python -m electriz.tools.bench --depth 4"""
import argparse
import time

import chess

from electriz.engine import Engine

# Toujours les mêmes positions, pour pouvoir comparer d'une version à l'autre
POSITIONS = [
    ("départ", chess.STARTING_FEN),
    ("Kiwipete", "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1"),
    ("finale", "8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - - 0 1"),
]


def main():
    parser = argparse.ArgumentParser(description="Benchmark du moteur")
    parser.add_argument("--depth", type=int, default=5, help="profondeur de recherche")
    args = parser.parse_args()

    total_noeuds = 0
    total_temps = 0.0

    for nom, fen in POSITIONS:
        engine = Engine()
        board = chess.Board(fen)

        debut = time.perf_counter()          # on démarre le chrono
        coup, score = engine.chercher(board, args.depth)
        temps = time.perf_counter() - debut  # on l'arrête

        total_noeuds += engine.noeuds
        total_temps += temps
        coup_san = board.san(coup) if coup is not None else "aucun"
        print(f"{nom:10} {coup_san:6} {engine.noeuds:7} noeuds  {temps:6.2f} s")

    print(f"TOTAL      {total_noeuds} noeuds  {total_temps:.2f} s"
          f"  ->  {total_noeuds / total_temps:,.0f} noeuds/s")


if __name__ == "__main__":
    main()