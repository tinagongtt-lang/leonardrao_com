from django import template

register = template.Library()


@register.filter
def split(value, arg=','):
    if not value:
        return []
    return [v.strip() for v in str(value).split(arg) if v.strip()]
