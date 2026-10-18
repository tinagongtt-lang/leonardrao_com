EMPTY = '.'
BLACK = 'b'
WHITE = 'w'


def empty_board(size):
    return EMPTY * (size * size)


def _idx(x, y, size):
    return y * size + x


def _neighbors(x, y, size):
    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        nx, ny = x + dx, y + dy
        if 0 <= nx < size and 0 <= ny < size:
            yield nx, ny


def _group(board, size, x, y):
    color = board[_idx(x, y, size)]
    group = set()
    liberties = set()
    stack = [(x, y)]
    while stack:
        cx, cy = stack.pop()
        if (cx, cy) in group:
            continue
        group.add((cx, cy))
        for nx, ny in _neighbors(cx, cy, size):
            v = board[_idx(nx, ny, size)]
            if v == EMPTY:
                liberties.add((nx, ny))
            elif v == color:
                stack.append((nx, ny))
    return group, liberties


def try_place(board, size, x, y, color):
    """Returns (new_board, captured_count) or None if illegal."""
    if board[_idx(x, y, size)] != EMPTY:
        return None
    opp = WHITE if color == BLACK else BLACK
    b = list(board)
    b[_idx(x, y, size)] = color
    captured = 0
    for nx, ny in _neighbors(x, y, size):
        if b[_idx(nx, ny, size)] == opp:
            g, libs = _group(''.join(b), size, nx, ny)
            if not libs:
                captured += len(g)
                for gx, gy in g:
                    b[_idx(gx, gy, size)] = EMPTY
    new_board = ''.join(b)
    own_group, own_libs = _group(new_board, size, x, y)
    if not own_libs:
        return None  # suicide
    return new_board, captured


def is_legal(board, size, x, y, color, ko_board):
    result = try_place(board, size, x, y, color)
    if result is None:
        return False
    if ko_board and result[0] == ko_board:
        return False
    return True


def legal_moves(board, size, color, ko_board):
    moves = []
    for y in range(size):
        for x in range(size):
            if board[_idx(x, y, size)] == EMPTY and is_legal(board, size, x, y, color, ko_board):
                moves.append((x, y))
    return moves


def score(board, size):
    """Chinese area scoring: stones + surrounded territory. Returns (black_area, white_area)."""
    visited = set()
    black_stones = sum(1 for c in board if c == BLACK)
    white_stones = sum(1 for c in board if c == WHITE)
    black_area = black_stones
    white_area = white_stones
    for y in range(size):
        for x in range(size):
            if board[_idx(x, y, size)] != EMPTY or (x, y) in visited:
                continue
            region = set()
            colors = set()
            stack = [(x, y)]
            while stack:
                cx, cy = stack.pop()
                if (cx, cy) in region:
                    continue
                region.add((cx, cy))
                for nx, ny in _neighbors(cx, cy, size):
                    v = board[_idx(nx, ny, size)]
                    if v == EMPTY:
                        stack.append((nx, ny))
                    else:
                        colors.add(v)
            visited |= region
            if colors == {BLACK}:
                black_area += len(region)
            elif colors == {WHITE}:
                white_area += len(region)
    return black_area, white_area
