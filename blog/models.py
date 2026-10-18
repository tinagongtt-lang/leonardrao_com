from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class BlogPost(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_posts', verbose_name=_('作者'))
    title = models.CharField(_('标题'), max_length=200)
    content = models.TextField(_('内容'))
    tags = models.CharField(_('标签'), max_length=255, blank=True, help_text=_('用逗号分隔多个标签'))
    created_at = models.DateTimeField(_('创建时间'), auto_now_add=True)
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('博客文章')
        verbose_name_plural = _('博客文章')
        indexes = [
            models.Index(fields=['author', '-created_at']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'username': self.author.username, 'pk': self.pk})


class AboutMe(models.Model):
    content = models.TextField(_('关于我'), default='')
    updated_at = models.DateTimeField(_('更新时间'), auto_now=True)

    class Meta:
        verbose_name = _('关于我')
        verbose_name_plural = _('关于我')

    def __str__(self):
        return _('关于我')

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1, defaults={'content': ''})
        return obj


class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments', verbose_name=_('博客'))
    author = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='comments', verbose_name=_('评论者'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies', verbose_name=_('回复目标'))
    content = models.TextField(_('评论内容'))
    created_at = models.DateTimeField(_('评论时间'), auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = _('评论')
        verbose_name_plural = _('评论')
        indexes = [
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['parent', '-created_at']),
        ]

    def __str__(self):
        return self.content[:50]
