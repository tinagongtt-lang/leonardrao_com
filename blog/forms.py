import re

import bleach
from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from captcha.fields import CaptchaField

from .models import BlogPost, AboutMe, Comment

_ALLOWED_TAGS = [
    'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'ul', 'ol', 'li', 'a', 'img', 'video', 'audio', 'source', 'div', 'span',
    'blockquote', 'pre', 'code', 's', 'del', 'hr', 'sub', 'sup',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
]
_ALLOWED_ATTRIBUTES = {
    '*': ['class'],
    'a': ['href', 'title', 'target'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'video': ['src', 'controls', 'width', 'height'],
    'audio': ['src', 'controls'],
    'source': ['src', 'type'],
}
_ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']


def sanitize_html(value):
    if not value:
        return value
    # Remove <script> blocks entirely before running bleach
    value = re.sub(r'<script[\s\S]*?</script>', '', value, flags=re.IGNORECASE)
    return bleach.clean(
        value,
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        protocols=_ALLOWED_PROTOCOLS,
        strip=True,
    )

User = get_user_model()


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'tags', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'maxlength': 200,
                'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
                'placeholder': _('请输入标题'),
            }),
            'tags': forms.TextInput(attrs={
                'maxlength': 255,
                'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
                'placeholder': _('用逗号分隔标签'),
            }),
            'content': forms.HiddenInput(attrs={
                'id': 'id_content',
            }),
        }

    def clean_content(self):
        return sanitize_html(self.cleaned_data.get('content', ''))


class AboutMeForm(forms.ModelForm):
    class Meta:
        model = AboutMe
        fields = ['content']
        widgets = {
            'content': forms.HiddenInput(attrs={
                'id': 'id_content',
            }),
        }

    def clean_content(self):
        return sanitize_html(self.cleaned_data.get('content', ''))


class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            'placeholder': _('用户名'),
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            'placeholder': _('密码'),
        })


class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
                'placeholder': _('用户名'),
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget = forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            'placeholder': _('密码'),
        })
        self.fields['password2'].widget = forms.PasswordInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            'placeholder': _('确认密码'),
        })


class CommentForm(forms.ModelForm):
    captcha = CaptchaField(label=_('验证码'))

    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4,
                'class': 'w-full px-3 py-2 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
                'placeholder': _('写下你的评论...'),
            }),
        }
