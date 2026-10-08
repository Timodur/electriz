import os
import random

import chess
import pytest

from electriz.engine import arena


def test_elo_estime():
    assert arena.elo_estime(0.5) == pytest.approx(0)
    assert arena.elo_estime(0.64) == pytest.approx(100, abs=2)
    assert arena.elo_estime(0.36) == pytest.approx(-100, abs=2)
    assert arena.elo_estime(0) is None and arena.elo_estime(1) is None


def test_ouverture_reproductible_et_valide():
    a = arena.ouverture_aleatoire(random.Random(7))
    b = arena.ouverture_aleatoire(random.Random(7))
    assert a.fen() == b.fen()
    assert a.ply() == arena.COUPS_OUVERTURE and not a.is_game_over()


def test_partie_se_termine_avec_un_resultat():
    joueur = arena.JoueurElectriz(1)
    board, res = arena.jouer_partie(joueur, joueur, chess.Board())
    assert res in ("1-0", "0-1", "1/2-1/2")
    assert board.ply() <= arena.MAX_DEMI_COUPS


def test_partie_commence_a_la_position_donnee():
    depart = arena.ouverture_aleatoire(random.Random(3))
    joueur = arena.JoueurElectriz(1)
    board, _ = arena.jouer_partie(joueur, joueur, depart)
    assert board.move_stack[:arena.COUPS_OUVERTURE] == depart.move_stack
    assert depart.ply() == arena.COUPS_OUVERTURE  # la position de départ n'est pas modifiée


def test_mat_en_1_est_gagne_par_les_blancs():
    depart = chess.Board("6k1/5ppp/8/8/8/8/8/R3K3 w - - 0 1")
    joueur = arena.JoueurElectriz(2)
    _, res = arena.jouer_partie(joueur, joueur, depart)
    assert res == "1-0"


def test_pgn_contient_les_noms_et_les_coups():
    depart = arena.ouverture_aleatoire(random.Random(1))
    joueur = arena.JoueurElectriz(1)
    board, res = arena.jouer_partie(joueur, joueur, depart)
    pgn = str(arena.pgn_de(board, "Blancs", "Noirs", res))
    assert '[White "Blancs"]' in pgn and f'[Result "{res}"]' in pgn


def test_creer_joueur():
    assert arena.creer_joueur("electriz:3", None).profondeur == 3
    with pytest.raises(SystemExit):
        arena.creer_joueur("inconnu:1", None)


def test_main_affiche_le_score(monkeypatch, capsys, tmp_path):
    pgn = tmp_path / "parties.pgn"
    monkeypatch.setattr("sys.argv", ["arena", "electriz:1", "electriz:2",
                                     "--parties", "2", "--graine", "1", "--pgn", str(pgn)])
    arena.main()
    sortie = capsys.readouterr().out
    assert "score" in sortie and "Electriz p1 contre Electriz p2" in sortie
    assert pgn.read_text().count("[Event") == 2  # une paire d'ouvertures = 2 parties


@pytest.mark.skipif(not os.path.exists(arena.CHEMIN_STOCKFISH), reason="Stockfish absent")
def test_stockfish_joue_un_coup_legal():
    sf = arena.JoueurStockfish(arena.CHEMIN_STOCKFISH, 1350, 0.02)
    try:
        board = chess.Board()
        assert sf.jouer(board) in board.legal_moves
    finally:
        sf.fermer()
