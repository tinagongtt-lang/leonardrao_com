from django import forms
from django.utils.translation import gettext_lazy as _
from captcha.fields import CaptchaField, CaptchaTextInput

from .models import Message


class MessageForm(forms.ModelForm):
    captcha = CaptchaField(
        label=_('验证码'),
        error_messages={'invalid': _('验证码错误')},
        widget=CaptchaTextInput(attrs={
            'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
        }),
    )

    class Meta:
        model = Message
        fields = ['name', 'content']
        widgets = {
            'name': forms.TextInput(attrs={
                'placeholder': _('你的昵称'),
                'maxlength': 64,
                'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            }),
            'content': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': _('写下你想说的话...'),
                'maxlength': 500,
                'class': 'w-full px-4 py-3 rounded-lg bg-white border border-slate-300 text-slate-900 focus:border-sky-500 outline-none dark:bg-slate-800 dark:border-slate-600 dark:text-white',
            }),
        }
