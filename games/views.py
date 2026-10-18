import secrets

from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .chess_logic import INITIAL_FEN
from .go_engine import empty_board
from .gomoku_engine import empty_board as gomoku_empty_board
from .models import ChessGame, GoGame, GomokuGame, XiangqiGame
from .xiangqi_logic import INITIAL_FEN as XQ_INITIAL_FEN


def index(request):
    return render(request, 'games/index.html')


def game2048(request):
    return render(request, 'games/2048.html')


def maze3d(request):
    return render(request, 'games/maze3d.html')


def _ensure_session(request):
    if not request.session.session_key:
        request.session.save()


def chess_home(request):
    return render(request, 'games/chess.html')


@require_POST
def chess_new(request):
    mode = request.POST.get('mode', 'ai')
    if mode not in ('ai', 'pvp'):
        mode = 'ai'
    try:
        difficulty = int(request.POST.get('level', '1'))
    except ValueError:
        difficulty = 1
    difficulty = max(1, min(difficulty, 4))
    _ensure_session(request)
    game = ChessGame.objects.create(
        code=secrets.token_hex(4),
        mode=mode,
        difficulty=difficulty,
        fen=INITIAL_FEN,
        status='waiting' if mode == 'pvp' else 'playing',
        white_key=request.session.session_key,
    )
    return redirect('games:chess_detail', code=game.code)


def chess_detail(request, code):
    game = get_object_or_404(ChessGame, code=code)
    _ensure_session(request)
    if game.mode == 'pvp' and not game.white_key:
        game.white_key = request.session.session_key
        game.save(update_fields=['white_key'])
    elif game.mode == 'ai' and not game.white_key:
        game.white_key = request.session.session_key
        game.status = 'playing'
        game.save(update_fields=['white_key', 'status'])
    return render(request, 'games/chess_board.html', {
        'game': game,
        'share_url': request.build_absolute_uri(),
    })


def xiangqi_home(request):
    return render(request, 'games/xiangqi.html')


@require_POST
def xiangqi_new(request):
    mode = request.POST.get('mode', 'ai')
    if mode not in ('ai', 'pvp'):
        mode = 'ai'
    try:
        difficulty = int(request.POST.get('level', '1'))
    except ValueError:
        difficulty = 1
    difficulty = max(1, min(difficulty, 4))
    _ensure_session(request)
    game = XiangqiGame.objects.create(
        code=secrets.token_hex(4),
        mode=mode,
        difficulty=difficulty,
        fen=XQ_INITIAL_FEN,
        status='waiting' if mode == 'pvp' else 'playing',
        red_key=request.session.session_key,
    )
    return redirect('games:xiangqi_detail', code=game.code)


def xiangqi_detail(request, code):
    game = get_object_or_404(XiangqiGame, code=code)
    _ensure_session(request)
    if game.mode == 'pvp' and not game.red_key:
        game.red_key = request.session.session_key
        game.save(update_fields=['red_key'])
    elif game.mode == 'ai' and not game.red_key:
        game.red_key = request.session.session_key
        game.status = 'playing'
        game.save(update_fields=['red_key', 'status'])
    return render(request, 'games/xiangqi_board.html', {
        'game': game,
        'share_url': request.build_absolute_uri(),
    })


def go_home(request):
    return render(request, 'games/go.html')


@require_POST
def go_new(request):
    mode = request.POST.get('mode', 'ai')
    if mode not in ('ai', 'pvp'):
        mode = 'ai'
    try:
        difficulty = int(request.POST.get('level', '1'))
        size = int(request.POST.get('size', '19'))
    except ValueError:
        difficulty, size = 1, 19
    difficulty = max(1, min(difficulty, 4))
    if size not in (9, 13, 19):
        size = 19
    _ensure_session(request)
    game = GoGame.objects.create(
        code=secrets.token_hex(4),
        mode=mode,
        difficulty=difficulty,
        size=size,
        board=empty_board(size),
        turn='black',
        status='waiting' if mode == 'pvp' else 'playing',
        black_key=request.session.session_key,
    )
    return redirect('games:go_detail', code=game.code)


def go_detail(request, code):
    game = get_object_or_404(GoGame, code=code)
    _ensure_session(request)
    if game.mode == 'pvp' and not game.black_key:
        game.black_key = request.session.session_key
        game.save(update_fields=['black_key'])
    elif game.mode == 'ai' and not game.black_key:
        game.black_key = request.session.session_key
        game.status = 'playing'
        game.save(update_fields=['black_key', 'status'])
    return render(request, 'games/go_board.html', {
        'game': game,
        'share_url': request.build_absolute_uri(),
    })


def gomoku_home(request):
    return render(request, 'games/gomoku.html')


@require_POST
def gomoku_new(request):
    mode = request.POST.get('mode', 'ai')
    if mode not in ('ai', 'pvp'):
        mode = 'ai'
    try:
        difficulty = int(request.POST.get('level', '1'))
    except ValueError:
        difficulty = 1
    difficulty = max(1, min(difficulty, 4))
    _ensure_session(request)
    game = GomokuGame.objects.create(
        code=secrets.token_hex(4),
        mode=mode,
        difficulty=difficulty,
        board=gomoku_empty_board(),
        turn='black',
        status='waiting' if mode == 'pvp' else 'playing',
        black_key=request.session.session_key,
    )
    return redirect('games:gomoku_detail', code=game.code)


def gomoku_detail(request, code):
    game = get_object_or_404(GomokuGame, code=code)
    _ensure_session(request)
    if game.mode == 'pvp' and not game.black_key:
        game.black_key = request.session.session_key
        game.save(update_fields=['black_key'])
    elif game.mode == 'ai' and not game.black_key:
        game.black_key = request.session.session_key
        game.status = 'playing'
        game.save(update_fields=['black_key', 'status'])
    return render(request, 'games/gomoku_board.html', {
        'game': game,
        'share_url': request.build_absolute_uri(),
    })
