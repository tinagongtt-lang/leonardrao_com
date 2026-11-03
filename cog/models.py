from django.conf import settings
from django.db import models


class CogSession(models.Model):
    id = models.CharField(primary_key=True, max_length=32)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='cog_sessions',
    )
    messages = models.JSONField(default=list)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']
        verbose_name = 'COG 会话'
        verbose_name_plural = 'COG 会话'

    def __str__(self):
        return f'{self.id} ({self.owner})'
