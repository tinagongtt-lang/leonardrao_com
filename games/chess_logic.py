import chess

from .chess_ai import choose_move

INITIAL_FEN = 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1'


def board_state(game, key):
    board = chess.Board(game.fen)
    turn = 'white' if board.turn == chess.WHITE else 'black'
    if game.mode == 'ai':
        color = 'white' if key == game.white_key else 'spectator'
    elif key == game.white_key:
        color = 'white'
    elif key == game.black_key:
        color = 'black'
    else:
        color = 'spectator'
    legal = [] if game.status == 'finished' else [m.uci() for m in board.legal_moves]
    return {
        'code': game.code,
        'mode': game.mode,
        'fen': game.fen,
        'turn': turn,
        'status': game.status,
        'result': game.result,
        'last_move': game.last_move,
        'legal_moves': legal,
        'check': board.is_check(),
        'color': color,
    }


def _finish_state(board, game):
    if board.is_checkmate():
        game.status = 'finished'
        game.result = 'white' if board.turn == chess.BLACK else 'black'
    elif board.is_stalemate() or board.is_insufficient_material() or board.is_seventyfive_moves():
        game.status = 'finished'
        game.result = 'draw'


def apply_move(game, key, move_uci):
    """Returns (state_dict, error_message_or_None)."""
    board = chess.Board(game.fen)

    if game.status == 'finished':
        return board_state(game, key), '对局已结束'
    if game.mode == 'pvp' and game.status == 'waiting':
        return board_state(game, key), '等待对手加入'

    mover_key = game.white_key if board.turn == chess.WHITE else game.black_key
    if key != mover_key:
        return board_state(game, key), '现在不是你的回合'

    try:
        move = chess.Move.from_uci(move_uci)
    except ValueError:
        return board_state(game, key), '无效的走法'

    if move not in board.legal_moves:
        return board_state(game, key), '该走法不合法'

    board.push(move)
    game.last_move = move.uci()
    game.fen = board.fen()
    if game.status == 'waiting':
        game.status = 'playing'
    _finish_state(board, game)

    if game.mode == 'ai' and game.status != 'finished':
        ai_move = choose_move(board, game.difficulty)
        if ai_move:
            board.push(ai_move)
            game.last_move = ai_move.uci()
            game.fen = board.fen()
            _finish_state(board, game)

    game.save()
    return board_state(game, key), None
