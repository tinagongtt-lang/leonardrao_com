from django.db import models
from django.utils import timezone


class Message(models.Model):
    name = models.CharField('昵称', max_length=64)
    content = models.TextField('留言内容')
    created_at = models.DateTimeField('发布时间', default=timezone.now)

    class Meta:
        ordering = ['-created_at']
        verbose_name = '留言'
        verbose_name_plural = '留言'

    def __str__(self):
        return f'{self.name} @ {self.created_at:%Y-%m-%d %H:%M}'
