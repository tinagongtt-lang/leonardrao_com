from django.conf import settings
from django import template

register = template.Library()


@register.filter
def localize_url(path, target_lang):
    """Replace the language prefix in path with target_lang."""
    codes = [code for code, _ in settings.LANGUAGES]
    parts = path.split('/')
    # parts[0] is '' because path starts with '/'
    if len(parts) > 1 and parts[1] in codes:
        parts = [''] + parts[2:]
    if target_lang and target_lang != settings.LANGUAGE_CODE:
        parts = ['', target_lang] + parts[1:]
    return '/'.join(parts) or '/'
