from django.conf import settings
from django.db import models
from django.utils import timezone


class Message(models.Model):
    name = models.CharField('昵称', max_length=64)
    content = models.TextField('留言内容')
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='guestbook_messages',
    )
    session_key = models.CharField(max_length=40, blank=True, default='')
    created_at = models.DateTimeField('发布时间', default=timezone.now)

    def can_delete(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        if self.user_id and request.user.is_authenticated and self.user_id == request.user.id:
            return True
        if not self.user_id and self.session_key and self.session_key == request.session.session_key:
            return True
        return False

    class Meta:
        ordering = ['-created_at']
        verbose_name = '留言'
        verbose_name_plural = '留言'

    def __str__(self):
        return f'{self.name} @ {self.created_at:%Y-%m-%d %H:%M}'
