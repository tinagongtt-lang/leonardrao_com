import json
import re

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer


from .models import ChatMessage, ChatRoom

MAX_LEN = 1000


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        user = self.scope.get('user')
        if not user or not user.is_authenticated:
            self.close()
            return
        self.group_name = f'chat_user_{user.id}'
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def notify(self, event):
        self.send(json.dumps({'type': 'notify'}))


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.code = self.scope['url_route']['kwargs']['code']
        self.group_name = f'chat_{self.code}'
        user = self.scope.get('user')
        try:
            self.room = ChatRoom.objects.get(code=self.code)
        except ChatRoom.DoesNotExist:
            self.close()
            return
        if not user or not user.is_authenticated or not self.room.members.filter(id=user.id).exists():
            self.close()
            return
        async_to_sync(self.channel_layer.group_add)(self.group_name, self.channel_name)
        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(self.group_name, self.channel_name)

    def receive(self, text_data):
        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            return
        msg_type = data.get('type')
        user = self.scope['user']
        if msg_type == 'message':
            content = re.sub(r'\s+', ' ', str(data.get('content', ''))).strip()[:MAX_LEN]
            if not content:
                return
            msg = ChatMessage.objects.create(room=self.room, sender=user, content=content)
        elif msg_type == 'image':
            url = str(data.get('url', ''))
            prefix = f'/media/chat/{self.room.code}/'
            if not url.startswith(prefix) or '..' in url:
                return
            msg = ChatMessage.objects.create(room=self.room, sender=user, msg_type='image', content=url)
        else:
            return
        async_to_sync(self.channel_layer.group_send)(
            self.group_name,
            {
                'type': 'broadcast_message',
                'msg_type': msg.msg_type,
                'sender': user.username,
                'content': msg.content,
                'time': msg.created_at.strftime('%H:%M'),
            },
        )

    def broadcast_message(self, event):
        self.send(json.dumps({
            'type': 'message',
            'msg_type': event.get('msg_type', 'text'),
            'sender': event['sender'],
            'content': event['content'],
            'time': event['time'],
        }))

    def member_kicked(self, event):
        self.send(json.dumps({'type': 'member_kicked', 'user_id': event['user_id']}))

    def room_deleted(self, event):
        self.send(json.dumps({'type': 'room_deleted'}))
