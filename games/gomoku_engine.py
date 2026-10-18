import random

EMPTY = '.'
BLACK = 'b'
WHITE = 'w'
SIZE = 15

DIRS = ((1, 0), (0, 1), (1, 1), (1, -1))


def empty_board():
    return EMPTY * (SIZE * SIZE)


def at(board, x, y):
    return board[y * SIZE + x]


def in_bounds(x, y):
    return 0 <= x < SIZE and 0 <= y < SIZE


def legal_moves(board):
    return [(x, y) for y in range(SIZE) for x in range(SIZE) if at(board, x, y) == EMPTY]


def candidate_moves(board):
    """Empty points within distance 2 of any stone (for AI speed)."""
    moves = set()
    for y in range(SIZE):
        for x in range(SIZE):
            if at(board, x, y) != EMPTY:
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        nx, ny = x + dx, y + dy
                        if in_bounds(nx, ny) and at(board, nx, ny) == EMPTY:
                            moves.add((nx, ny))
    return list(moves) or legal_moves(board)


def place(board, x, y, color):
    if not in_bounds(x, y) or at(board, x, y) != EMPTY:
        return None
    b = list(board)
    b[y * SIZE + x] = color
    return ''.join(b)


def line_count(board, x, y, dx, dy, color):
    """Count consecutive stones of color through (x,y) along direction."""
    count = 1
    nx, ny = x + dx, y + dy
    while in_bounds(nx, ny) and at(board, nx, ny) == color:
        count += 1
        nx += dx
        ny += dy
    open_ends = 0
    if in_bounds(nx, ny) and at(board, nx, ny) == EMPTY:
        open_ends += 1
    nx, ny = x - dx, y - dy
    while in_bounds(nx, ny) and at(board, nx, ny) == color:
        count += 1
        nx -= dx
        ny -= dy
    if in_bounds(nx, ny) and at(board, nx, ny) == EMPTY:
        open_ends += 1
    return count, open_ends


def wins(board, x, y, color):
    return any(line_count(board, x, y, dx, dy, color)[0] >= 5 for dx, dy in DIRS)


def board_full(board):
    return EMPTY not in board


PATTERN_SCORES = {
    (5, 0): 100000, (5, 1): 100000, (5, 2): 100000,
    (4, 2): 15000, (4, 1): 8000, (4, 0): 1500,
    (3, 2): 2500, (3, 1): 500, (3, 0): 100,
    (2, 2): 200, (2, 1): 50, (2, 0): 10,
    (1, 2): 20, (1, 1): 5, (1, 0): 1,
}


def move_score(board, x, y, color):
    opp = WHITE if color == BLACK else BLACK
    attack = sum(PATTERN_SCORES.get(line_count(board, x, y, dx, dy, color), (0, 0))
                 for dx, dy in DIRS)
    defense = sum(PATTERN_SCORES.get(line_count(board, x, y, dx, dy, opp), (0, 0))
                  for dx, dy in DIRS)
    center = 14 - (abs(x - 7) + abs(y - 7))
    return attack + defense * 0.9 + center * 2


def choose_move(board, color, level):
    moves = legal_moves(board)
    if not moves:
        return None
    if level <= 1:
        return random_choice_near(board)
    cands = candidate_moves(board)
    if level == 2:
        # take wins, block opponent wins
        for x, y in cands:
            nb = place(board, x, y, color)
            if nb and wins(nb, x, y, color):
                return (x, y)
        opp = WHITE if color == BLACK else BLACK
        for x, y in cands:
            nb = place(board, x, y, opp)
            if nb and wins(nb, x, y, opp):
                return (x, y)
        return random_choice(cands)
    return max(cands, key=lambda m: move_score(board, m[0], m[1], color))


def random_choice(lst):
    return random.choice(lst)


def random_choice_near(board):
    cands = candidate_moves(board)
    return random.choice(cands)
