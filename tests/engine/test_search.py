import chess
import pytest
from positions import POSITIONS

from electriz.engine import MATE_SCORE

BERGER = "r1bqkbnr/pppp1ppp/2n5/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4"


@pytest.mark.parametrize("profondeur", [1, 2, 3])
def test_trouve_le_coup_du_berger(engine, profondeur):
    """Bug corrigé : l'ancienne version jouait Fxf7+ au lieu de Dxf7#."""
    board = chess.Board(BERGER)
    coup, score = engine.chercher(board, profondeur)
    assert board.san(coup) == "Qxf7#"
    assert score == MATE_SCORE - 1


def test_mat_du_couloir_pour_les_noirs(engine):
    board = chess.Board("3r2k1/5ppp/8/8/8/8/5PPP/6K1 b - - 0 1")
    coup, score = engine.chercher(board, 2)
    assert board.san(coup) == "Rd1#"
    assert score == -(MATE_SCORE - 1)


def test_pat_vaut_zero(engine):
    pat = chess.Board("7k/5Q2/6K1/8/8/8/8/8 b - - 0 1")
    assert pat.is_stalemate()
    assert engine.alphabeta(pat, 3) == 0


def test_partie_finie_pas_de_coup(engine):
    mat = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    assert mat.is_checkmate()
    assert engine.chercher(mat, 2)[0] is None


@pytest.mark.parametrize("fen", POSITIONS)
@pytest.mark.parametrize("profondeur", [1, 2, 3])
def test_alphabeta_egal_minimax(engine, fen, profondeur):
    """Wikipédia : l'élagage alpha-bêta ne change pas le résultat de minimax."""
    board = chess.Board(fen)
    assert engine.alphabeta(board, profondeur) == engine.minimax(board, profondeur)
    assert board.fen() == chess.Board(fen).fen()  # la recherche ne modifie pas l'échiquier


def test_alphabeta_visite_moins_de_noeuds(engine):
    board = chess.Board(POSITIONS[2])
    engine.noeuds = 0
    engine.minimax(board, 3)
    noeuds_minimax = engine.noeuds
    engine.noeuds = 0
    engine.alphabeta(board, 3)
    assert engine.noeuds < noeuds_minimax / 5
