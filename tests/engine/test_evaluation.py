import chess
import pytest

from src.engine.evaluation import MATE_SCORE, Engine

POSITIONS = [
    chess.STARTING_FEN,
    # Italienne
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3",
    # Kiwipete (position de test de perft), https://www.chessprogramming.org/Perft_Results
    "r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq - 0 1",
    # Finale tour + pions
    "8/5k2/3p4/1p1Pp2p/pP2Pp1P/P4P1K/8/8 b - - 99 50",
]


@pytest.fixture
def engine():
    return Engine()


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
