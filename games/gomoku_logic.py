from .gomoku_engine import BLACK, SIZE, choose_move, legal_moves, place, wins


def board_state(game, key):
    if game.mode == 'ai':
        color = 'black' if key == game.black_key else 'spectator'
    elif key == game.black_key:
        color = 'black'
    elif key == game.white_key:
        color = 'white'
    else:
        color = 'spectator'
    turn_color = BLACK if game.turn == 'black' else 'w'
    legal = [] if game.status == 'finished' else [f'{x},{y}' for x, y in legal_moves(game.board)]
    return {
        'code': game.code,
        'mode': game.mode,
        'size': SIZE,
        'board': game.board,
        'turn': game.turn,
        'status': game.status,
        'result': game.result,
        'last_move': game.last_move,
        'legal_moves': legal,
        'color': color,
    }


def _play(game, color_char, x, y):
    nb = place(game.board, x, y, color_char)
    if nb is None:
        return False
    game.board = nb
    game.last_move = f'{x},{y}'
    if wins(nb, x, y, color_char):
        game.status = 'finished'
        game.result = 'black' if color_char == BLACK else 'white'
    elif '.' not in nb:
        game.status = 'finished'
        game.result = 'draw'
    game.turn = 'white' if game.turn == 'black' else 'black'
    return True


def apply_move(game, key, move_str):
    """Returns (state_dict, error_message_or_None)."""
    if game.status == 'finished':
        return board_state(game, key), '对局已结束'
    if game.mode == 'pvp' and game.status == 'waiting':
        return board_state(game, key), '等待对手加入'

    mover_key = game.black_key if game.turn == 'black' else game.white_key
    if key != mover_key:
        return board_state(game, key), '现在不是你的回合'

    if move_str == 'resign':
        game.status = 'finished'
        game.result = 'white' if game.turn == 'black' else 'black'
        game.save()
        return board_state(game, key), None

    try:
        x, y = (int(v) for v in move_str.split(','))
    except ValueError:
        return board_state(game, key), '无效的走法'

    color = BLACK if game.turn == 'black' else 'w'
    if not _play(game, color, x, y):
        return board_state(game, key), '该位置不能落子'

    if game.mode == 'ai' and game.status != 'finished':
        ai_color = BLACK if game.turn == 'black' else 'w'
        ai = choose_move(game.board, ai_color, game.difficulty)
        if ai is None:
            game.status = 'finished'
            game.result = 'draw'
        else:
            _play(game, ai_color, ai[0], ai[1])

    game.save()
    return board_state(game, key), None
