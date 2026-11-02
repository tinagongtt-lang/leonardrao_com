from .models import FriendlyLink, Visitor


def visit_count(request):
    return {
        'visit_count': Visitor.objects.count(),
        'friendly_links': FriendlyLink.objects.all(),
    }
