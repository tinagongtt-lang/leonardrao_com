import cchess

from .xiangqi_ai import choose_move

INITIAL_FEN = cchess.FULL_INIT_FEN


def _load_board(fen):
    board = cchess.ChessBoard(fen)
    board.set_move_color(cchess.BLACK if fen.rstrip().endswith(' b') else cchess.RED)
    return board


def _is_in_check(board):
    nb = board.copy()
    nb.next_turn()
    return nb.is_checking()


def board_state(game, key):
    board = _load_board(game.fen)
    turn = 'red' if board.move_player == cchess.RED else 'black'
    if game.mode == 'ai':
        color = 'red' if key == game.red_key else 'spectator'
    elif key == game.red_key:
        color = 'red'
    elif key == game.black_key:
        color = 'black'
    else:
        color = 'spectator'
    legal = [] if game.status == 'finished' else [cchess.pos2iccs(*m) for m in board.create_moves()]
    return {
        'code': game.code,
        'mode': game.mode,
        'fen': game.fen,
        'turn': turn,
        'status': game.status,
        'result': game.result,
        'last_move': game.last_move,
        'legal_moves': legal,
        'check': _is_in_check(board),
        'color': color,
    }


def _finish_state(board, game):
    # call after board.next_turn(): move_player is the side to move
    if board.no_moves():
        game.status = 'finished'
        game.result = 'red' if board.move_player == cchess.BLACK else 'black'


def apply_move(game, key, move_str):
    """Returns (state_dict, error_message_or_None)."""
    board = _load_board(game.fen)

    if game.status == 'finished':
        return board_state(game, key), '对局已结束'
    if game.mode == 'pvp' and game.status == 'waiting':
        return board_state(game, key), '等待对手加入'

    mover_key = game.red_key if board.move_player == cchess.RED else game.black_key
    if key != mover_key:
        return board_state(game, key), '现在不是你的回合'

    try:
        pos_from, pos_to = cchess.iccs2pos(move_str)
    except Exception:
        return board_state(game, key), '无效的走法'

    if not board.is_valid_move(pos_from, pos_to):
        return board_state(game, key), '该走法不合法'

    board.move(pos_from, pos_to)
    board.next_turn()
    game.last_move = move_str
    game.fen = board.to_fen()
    if game.status == 'waiting':
        game.status = 'playing'
    _finish_state(board, game)

    if game.mode == 'ai' and game.status != 'finished':
        ai_move = choose_move(board, game.difficulty)
        if ai_move:
            board.move(*ai_move)
            board.next_turn()
            game.last_move = cchess.pos2iccs(*ai_move)
            game.fen = board.to_fen()
            _finish_state(board, game)

    game.save()
    return board_state(game, key), None
