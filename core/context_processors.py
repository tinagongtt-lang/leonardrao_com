from .models import FriendlyLink, VisitCounter


def visit_count(request):
    counter, _ = VisitCounter.objects.get_or_create(name='total', defaults={'count': 0})
    return {
        'visit_count': counter.count,
        'friendly_links': FriendlyLink.objects.all(),
    }
