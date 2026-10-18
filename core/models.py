from django.db import models


class VisitCounter(models.Model):
    name = models.CharField(max_length=32, unique=True, default='total')
    count = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = '访问计数'
        verbose_name_plural = '访问计数'

    def __str__(self):
        return f'{self.name}: {self.count}'


class FriendlyLink(models.Model):
    name = models.CharField(max_length=64, verbose_name='名称')
    url = models.URLField(verbose_name='链接')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = '友情链接'
        verbose_name_plural = '友情链接'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
        ]

    def __str__(self):
        return self.name
