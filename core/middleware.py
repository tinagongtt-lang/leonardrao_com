from django.db.models import F

from .models import VisitCounter


class VisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(('/admin/', '/static/', '/api/', '/favicon.ico')):
            VisitCounter.objects.filter(name='total').update(count=F('count') + 1)
        response = self.get_response(request)
        return response
