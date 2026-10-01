"""Positions de test partagées."""

import chess

POSITIONS = [
    chess.STARTING_FEN,
    # Italienne
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    # Kiwipete (position de test de perft), https://www.chessprogramming.org/Perft_Results
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    # Finale tour + pions
    "8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8 b - - 99 50",
]
