import random

from django.contrib.auth.models import User
from django.db import models


class ChatProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_profile')
    friend_code = models.CharField(max_length=10, unique=True)
    friends = models.ManyToManyField('self', symmetrical=True, blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.friend_code})'


def generate_friend_code():
    while True:
        code = str(random.randint(10000000, 99999999))
        if not ChatProfile.objects.filter(friend_code=code).exists():
            return code


def get_profile(user):
    profile, _ = ChatProfile.objects.get_or_create(
        user=user,
        defaults={'friend_code': generate_friend_code()},
    )
    return profile


class ChatRoom(models.Model):
    code = models.CharField(max_length=16, unique=True)
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_rooms')
    members = models.ManyToManyField(User, related_name='chat_rooms')
    admins = models.ManyToManyField(User, related_name='admin_rooms', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_admin_or_owner(self, user):
        return user.id == self.owner_id or self.admins.filter(id=user.id).exists()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class FriendRequest(models.Model):
    STATUS = [('pending', '待处理'), ('accepted', '已同意'), ('declined', '已拒绝')]

    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_friend_requests')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_friend_requests')
    status = models.CharField(max_length=10, choices=STATUS, default='pending', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class RoomInvite(models.Model):
    STATUS = [
        ('awaiting', '待群主确认'),
        ('pending', '待处理'),
        ('accepted', '已同意'),
        ('declined', '已拒绝'),
    ]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='invites')
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_room_invites')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_room_invites')
    status = models.CharField(max_length=10, choices=STATUS, default='awaiting', db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']


class ChatMessage(models.Model):
    MSG_TYPES = [('text', '文字'), ('image', '图片')]

    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_messages')
    msg_type = models.CharField(max_length=10, choices=MSG_TYPES, default='text')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
        indexes = [models.Index(fields=['room', 'created_at'])]

    def __str__(self):
        return f'{self.sender.username}: {self.content[:30]}'
