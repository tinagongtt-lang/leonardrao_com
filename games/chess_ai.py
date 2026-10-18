import random

import chess

PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}


def _material_score(board):
    score = 0
    for square, piece in board.piece_map().items():
        value = PIECE_VALUES[piece.piece_type]
        score += value if piece.color == chess.WHITE else -value
    return score


def _minimax(board, depth, alpha, beta):
    if depth == 0 or board.is_game_over():
        if board.is_checkmate():
            return -99999 if board.turn == chess.WHITE else 99999
        if board.is_stalemate() or board.is_insufficient_material():
            return 0
        return _material_score(board)

    if board.turn == chess.WHITE:
        best = -100000
        for move in board.legal_moves:
            board.push(move)
            best = max(best, _minimax(board, depth - 1, alpha, beta))
            board.pop()
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    best = 100000
    for move in board.legal_moves:
        board.push(move)
        best = min(best, _minimax(board, depth - 1, alpha, beta))
        board.pop()
        beta = min(beta, best)
        if beta <= alpha:
            break
    return best


def choose_move(board, level):
    legal = list(board.legal_moves)
    if not legal:
        return None
    if level <= 1:
        return random.choice(legal)
    if level == 2:
        captures = [m for m in legal if board.is_capture(m)]
        if captures:
            return max(captures, key=lambda m: PIECE_VALUES[board.piece_type_at(m.to_square) or chess.PAWN])
        return random.choice(legal)
    depth = {3: 2, 4: 3}.get(level, 2)
    best_score = -100000
    best_moves = []
    for move in legal:
        board.push(move)
        score = _minimax(board, depth - 1, -100000, 100000)
        board.pop()
        score += random.uniform(0, 10)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)
    return random.choice(best_moves)
