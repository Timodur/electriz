import io

import chess

from electriz.uci.loop import UCI


def lancer(commandes):
    sortie = io.StringIO()
    UCI(entree=io.StringIO(commandes), sortie=sortie).run()
    return sortie.getvalue().splitlines()


def test_handshake():
    lignes = lancer("uci\nisready\nquit\n")
    assert "uciok" in lignes and "readyok" in lignes
    assert any(l.startswith("id name") for l in lignes)


def test_position_et_coups():
    u = UCI(entree=io.StringIO(""), sortie=io.StringIO())
    u.traiter("position startpos moves e2e4 e7e5")
    assert u.board.fullmove_number == 2 and u.board.turn == chess.WHITE


def test_position_fen():
    fen = "8/8/8/8/8/k7/8/K6R w - - 0 1"
    u = UCI(entree=io.StringIO(""), sortie=io.StringIO())
    u.traiter(f"position fen {fen}")
    assert u.board.fen() == fen


def test_go_depth_renvoie_un_coup_legal():
    lignes = lancer("position startpos\ngo depth 2\nquit\n")
    best = [l for l in lignes if l.startswith("bestmove")][0].split()[1]
    assert chess.Move.from_uci(best) in chess.Board().legal_moves


def test_mat_en_1():
    lignes = lancer("position fen 6k1/5ppp/8/8/8/8/8/R3K3 w - - 0 1\ngo depth 3\nquit\n")
    assert "bestmove a1a8" in lignes
    assert any("score mate 1" in l for l in lignes)


def test_go_movetime_respecte_le_budget():
    import time
    t = time.perf_counter()
    lignes = lancer("position startpos\ngo movetime 300\nquit\n")
    assert time.perf_counter() - t < 2
    assert any(l.startswith("bestmove") for l in lignes)


def test_partie_finie():
    lignes = lancer("position fen 7k/5Q2/6K1/8/8/8/8/8 b - - 0 1\ngo depth 2\nquit\n")
    assert "bestmove 0000" in lignes
