import random

import cchess

PIECE_VALUES = {
    'p': 100,
    'a': 120,
    'b': 120,
    'n': 270,
    'c': 300,
    'r': 600,
    'k': 10000,
}


def _material_score(board):
    score = 0
    for color in (cchess.RED, cchess.BLACK):
        sign = 1 if color == cchess.RED else -1
        for piece in board.get_pieces(color):
            score += sign * PIECE_VALUES.get(piece.fench.lower(), 0)
    return score


def _minimax(board, depth, alpha, beta):
    if board.no_moves():
        return -99999 if board.move_player == cchess.RED else 99999
    if depth == 0:
        return _material_score(board)
    if board.move_player == cchess.RED:
        best = -100000
        for move in board.create_moves():
            nb = board.copy()
            nb.move(*move)
            nb.next_turn()
            best = max(best, _minimax(nb, depth - 1, alpha, beta))
            alpha = max(alpha, best)
            if beta <= alpha:
                break
        return best
    best = 100000
    for move in board.create_moves():
        nb = board.copy()
        nb.move(*move)
        nb.next_turn()
        best = min(best, _minimax(nb, depth - 1, alpha, beta))
        beta = min(beta, best)
        if beta <= alpha:
            break
    return best


def choose_move(board, level):
    legal = list(board.create_moves())
    if not legal:
        return None
    if level <= 1:
        return random.choice(legal)
    if level == 2:
        captures = []
        for move in legal:
            target = board.get_piece(move[1])
            if target is not None:
                captures.append((PIECE_VALUES.get(target.fench.lower(), 0), move))
        if captures:
            return max(captures, key=lambda t: t[0])[1]
        return random.choice(legal)
    depth = {3: 2, 4: 3}.get(level, 2)
    best_score = -100000
    best_moves = []
    for move in legal:
        nb = board.copy()
        nb.move(*move)
        nb.next_turn()
        score = _minimax(nb, depth - 1, -100000, 100000)
        score += random.uniform(0, 10)
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            best_moves.append(move)
    return random.choice(best_moves)
