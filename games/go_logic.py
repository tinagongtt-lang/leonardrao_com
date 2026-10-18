import random

from .go_engine import BLACK, EMPTY, WHITE, _group, _idx, legal_moves, score, try_place

KOMI = 7.5


def board_state(game, key):
    if game.mode == 'ai':
        color = 'black' if key == game.black_key else 'spectator'
    elif key == game.black_key:
        color = 'black'
    elif key == game.white_key:
        color = 'white'
    else:
        color = 'spectator'
    turn_color = BLACK if game.turn == 'black' else WHITE
    legal = [] if game.status == 'finished' else legal_moves(game.board, game.size, turn_color, game.ko_board)
    return {
        'code': game.code,
        'mode': game.mode,
        'size': game.size,
        'board': game.board,
        'turn': game.turn,
        'status': game.status,
        'result': game.result,
        'last_move': game.last_move,
        'captures_b': game.captures_b,
        'captures_w': game.captures_w,
        'legal_moves': [f'{x},{y}' for x, y in legal],
        'color': color,
    }


def _apply_stone(game, color, x, y):
    result = try_place(game.board, game.size, x, y, color)
    if result is None:
        return False
    new_board, captured = result
    if game.ko_board and new_board == game.ko_board:
        return False  # ko
    game.ko_board = game.board
    game.board = new_board
    game.pass_streak = 0
    game.last_move = f'{x},{y}'
    if color == BLACK:
        game.captures_b += captured
    else:
        game.captures_w += captured
    game.turn = 'white' if color == BLACK else 'black'
    return True


def _finish_by_area(game):
    b, w = score(game.board, game.size)
    w += KOMI
    game.status = 'finished'
    game.result = 'black' if b > w else 'white'


def _ai_move(game):
    color = BLACK if game.turn == 'black' else WHITE
    moves = legal_moves(game.board, game.size, color, game.ko_board)
    if not moves:
        return None
    if game.difficulty <= 1:
        return random.choice(moves)

    def move_score(x, y):
        res = try_place(game.board, game.size, x, y, color)
        if res is None:
            return -1
        new_board, captured = res
        s = captured * 100
        # avoid self-atari
        g, libs = _group(new_board, game.size, x, y)
        if len(libs) == 1:
            s -= 80 if game.difficulty >= 3 else 20
        elif len(libs) == 2:
            s += 10
        else:
            s += 5
        # put opponent groups into atari
        if game.difficulty >= 4:
            opp = WHITE if color == BLACK else BLACK
            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < game.size and 0 <= ny < game.size and new_board[_idx(nx, ny, game.size)] == opp:
                    og, olibs = _group(new_board, game.size, nx, ny)
                    if len(olibs) == 1:
                        s += 60
        # edge penalty for first moves on edge
        edge = min(x, y, game.size - 1 - x, game.size - 1 - y)
        s += edge * (3 if game.difficulty >= 3 else 1)
        return s + random.uniform(0, 5)

    return max(moves, key=lambda m: move_score(*m))


def apply_move(game, key, move_str):
    """Returns (state_dict, error_message_or_None)."""
    if game.status == 'finished':
        return board_state(game, key), '对局已结束'
    if game.mode == 'pvp' and game.status == 'waiting':
        return board_state(game, key), '等待对手加入'

    mover_key = game.black_key if game.turn == 'black' else game.white_key
    if key != mover_key:
        return board_state(game, key), '现在不是你的回合'

    color = BLACK if game.turn == 'black' else WHITE

    if move_str == 'resign':
        game.status = 'finished'
        game.result = 'white' if game.turn == 'black' else 'black'
        game.save()
        return board_state(game, key), None

    if move_str == 'pass':
        game.ko_board = game.board
        game.pass_streak += 1
        game.last_move = 'pass'
        game.turn = 'white' if game.turn == 'black' else 'black'
        if game.pass_streak >= 2:
            _finish_by_area(game)
    else:
        try:
            x, y = (int(v) for v in move_str.split(','))
        except ValueError:
            return board_state(game, key), '无效的走法'
        if not (0 <= x < game.size and 0 <= y < game.size):
            return board_state(game, key), '无效的走法'
        if not _apply_stone(game, color, x, y):
            return board_state(game, key), '该位置不能落子'

    if game.mode == 'ai' and game.status != 'finished':
        ai_color = BLACK if game.turn == 'black' else WHITE
        ai = _ai_move(game)
        if ai is None:
            game.pass_streak += 1
            game.last_move = 'pass'
            game.turn = 'white' if game.turn == 'black' else 'black'
            if game.pass_streak >= 2:
                _finish_by_area(game)
        else:
            _apply_stone(game, ai_color, ai[0], ai[1])

    game.save()
    return board_state(game, key), None
