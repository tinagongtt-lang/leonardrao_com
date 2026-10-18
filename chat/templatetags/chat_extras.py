import re

from django import template
from django.utils.html import escape
from django.utils.safestring import mark_safe

register = template.Library()

_TLD = r'(?:com|net|org|io|dev|app|ai|me|info|biz|gov|edu|cn|jp|kr|us|uk|xyz|site|cc|tv|top|vip|shop|wiki|blog|club|online|tech|live|ink|red|blue|mobi|asia)'
_PATH = r"(?:/[A-Za-z0-9\-._~:/?#@!$&'()*+,;=%]*)?"
URL_RE = re.compile(
    r'(https?://[^\s<>"\']+'
    r'|\d{1,3}(?:\.\d{1,3}){3}(?::\d{1,5})?' + _PATH
    + r'|[a-zA-Z0-9][-a-zA-Z0-9]*(?:\.[a-zA-Z0-9][-a-zA-Z0-9]*)*\.' + _TLD + r'\b' + _PATH + r')',
    re.IGNORECASE,
)


@register.filter
def linkify(text, link_class='text-sky-600 dark:text-sky-400 underline hover:opacity-80 break-all'):
    parts = URL_RE.split(str(text))
    out = []
    for i, part in enumerate(parts):
        if i % 2 == 1:
            if re.match(r'https?://', part):
                href = part
            elif re.match(r'\d{1,3}(?:\.\d{1,3}){3}', part):
                href = f'http://{part}'
            else:
                href = f'https://{part}'
            out.append(
                f'<a href="{escape(href)}" target="_blank" rel="noopener noreferrer" '
                f'class="{link_class}">{escape(part)}</a>'
            )
        else:
            out.append(escape(part))
    return mark_safe(''.join(out))
