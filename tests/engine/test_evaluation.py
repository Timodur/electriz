import chess
import pytest
from positions import POSITIONS


def test_position_initiale_equilibree(engine):
    assert engine.evaluer_position(chess.Board()) == 0


@pytest.mark.parametrize("fen", POSITIONS)
def test_symetrie_couleurs(engine, fen):
    """Échanger les couleurs (board.mirror()) doit inverser le score."""
    board = chess.Board(fen)
    assert engine.evaluer_position(board) == -engine.evaluer_position(board.mirror())


def test_roi_prefere_le_roque(engine):
    """Le roi blanc doit être mieux en g1 qu'en e2 (bug corrigé : table inversée)."""
    roque = chess.Board("4k3/8/8/8/8/8/8/6K1 w - - 0 1")
    avance = chess.Board("4k3/8/8/8/8/8/4K3/8 w - - 0 1")
    # Avec dames, pour rester en milieu de partie
    roque.set_piece_at(chess.D1, chess.Piece(chess.QUEEN, chess.WHITE))
    roque.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))
    avance.set_piece_at(chess.D1, chess.Piece(chess.QUEEN, chess.WHITE))
    avance.set_piece_at(chess.A1, chess.Piece(chess.ROOK, chess.WHITE))
    assert engine.evaluer_position(roque) > engine.evaluer_position(avance)


def test_detection_finale(engine):
    assert not engine.est_finale(chess.Board())
    assert engine.est_finale(chess.Board("4k3/8/8/8/8/8/8/4K2R w - - 0 1"))
