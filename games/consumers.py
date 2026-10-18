import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .chess_logic import apply_move, board_state
from .go_logic import apply_move as go_apply_move
from .go_logic import board_state as go_board_state
from .gomoku_logic import apply_move as gomoku_apply_move
from .gomoku_logic import board_state as gomoku_board_state
from .models import ChessGame, GoGame, GomokuGame, XiangqiGame
from .xiangqi_logic import apply_move as xq_apply_move
from .xiangqi_logic import board_state as xq_board_state


class ChessConsumer(WebsocketConsumer):
    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group_name = f'chess_{self.code}'
        try:
            self.game = ChessGame.objects.get(code=self.code)
        except ChessGame.DoesNotExist:
            self.close()
            return
        session = self.scope['session']
        if not session.session_key:
            session.save()
        self.key = session.session_key
        self._join_game()
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        self.group_send_state()

    def _join_game(self):
        game = self.game
        changed = False
        if game.mode == 'ai':
            if not game.white_key:
                game.white_key = self.key
                game.status = 'playing'
                changed = True
        else:
            if not game.white_key:
                game.white_key = self.key
                changed = True
            elif self.key != game.white_key and not game.black_key:
                game.black_key = self.key
                game.status = 'playing'
                changed = True
        if changed:
            game.save()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def group_send_state(self):
        from channels.layers import get_channel_layer
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            self.group_name,
            {'type': 'broadcast_state'},
        )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get('type') == 'move':
            state, error = apply_move(self.game, self.key, data.get('move', ''))
            if error:
                self.send(json.dumps({'type': 'error', 'error': error, 'state': state}))
            self.group_send_state()

    def broadcast_state(self, event):
        self.game.refresh_from_db()
        self.send(json.dumps({
            'type': 'state',
            'state': board_state(self.game, self.key),
        }))


class XiangqiConsumer(WebsocketConsumer):
    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group_name = f'xiangqi_{self.code}'
        try:
            self.game = XiangqiGame.objects.get(code=self.code)
        except XiangqiGame.DoesNotExist:
            self.close()
            return
        session = self.scope['session']
        if not session.session_key:
            session.save()
        self.key = session.session_key
        self._join_game()
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        self.group_send_state()

    def _join_game(self):
        game = self.game
        changed = False
        if game.mode == 'ai':
            if not game.red_key:
                game.red_key = self.key
                game.status = 'playing'
                changed = True
        else:
            if not game.red_key:
                game.red_key = self.key
                changed = True
            elif self.key != game.red_key and not game.black_key:
                game.black_key = self.key
                game.status = 'playing'
                changed = True
        if changed:
            game.save()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def group_send_state(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {'type': 'broadcast_state'},
        )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get('type') == 'move':
            state, error = xq_apply_move(self.game, self.key, data.get('move', ''))
            if error:
                self.send(json.dumps({'type': 'error', 'error': error, 'state': state}))
            self.group_send_state()

    def broadcast_state(self, event):
        self.game.refresh_from_db()
        self.send(json.dumps({
            'type': 'state',
            'state': xq_board_state(self.game, self.key),
        }))


class GoConsumer(WebsocketConsumer):
    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group_name = f'go_{self.code}'
        try:
            self.game = GoGame.objects.get(code=self.code)
        except GoGame.DoesNotExist:
            self.close()
            return
        session = self.scope['session']
        if not session.session_key:
            session.save()
        self.key = session.session_key
        self._join_game()
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        self.group_send_state()

    def _join_game(self):
        game = self.game
        changed = False
        if game.mode == 'ai':
            if not game.black_key:
                game.black_key = self.key
                game.status = 'playing'
                changed = True
        else:
            if not game.black_key:
                game.black_key = self.key
                changed = True
            elif self.key != game.black_key and not game.white_key:
                game.white_key = self.key
                game.status = 'playing'
                changed = True
        if changed:
            game.save()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def group_send_state(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {'type': 'broadcast_state'},
        )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get('type') == 'move':
            state, error = go_apply_move(self.game, self.key, data.get('move', ''))
            if error:
                self.send(json.dumps({'type': 'error', 'error': error, 'state': state}))
            self.group_send_state()

    def broadcast_state(self, event):
        self.game.refresh_from_db()
        self.send(json.dumps({
            'type': 'state',
            'state': go_board_state(self.game, self.key),
        }))


class GomokuConsumer(WebsocketConsumer):
    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group_name = f'gomoku_{self.code}'
        try:
            self.game = GomokuGame.objects.get(code=self.code)
        except GomokuGame.DoesNotExist:
            self.close()
            return
        session = self.scope['session']
        if not session.session_key:
            session.save()
        self.key = session.session_key
        self._join_game()
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()
        self.group_send_state()

    def _join_game(self):
        game = self.game
        changed = False
        if game.mode == 'ai':
            if not game.black_key:
                game.black_key = self.key
                game.status = 'playing'
                changed = True
        else:
            if not game.black_key:
                game.black_key = self.key
                changed = True
            elif self.key != game.black_key and not game.white_key:
                game.white_key = self.key
                game.status = 'playing'
                changed = True
        if changed:
            game.save()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def group_send_state(self):
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {'type': 'broadcast_state'},
        )

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        if data.get('type') == 'move':
            state, error = gomoku_apply_move(self.game, self.key, data.get('move', ''))
            if error:
                self.send(json.dumps({'type': 'error', 'error': error, 'state': state}))
            self.group_send_state()

    def broadcast_state(self, event):
        self.game.refresh_from_db()
        self.send(json.dumps({
            'type': 'state',
            'state': gomoku_board_state(self.game, self.key),
        }))
