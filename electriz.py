import chess
import random
board = chess.Board()

move = random.choice(list(board.legal_moves))
board.push(move)

print(board)