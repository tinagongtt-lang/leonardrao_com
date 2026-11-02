from .models import Visitor


class VisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(('/admin/', '/static/', '/api/', '/favicon.ico')):
            if request.user.is_authenticated:
                key = f'u{request.user.pk}'
            else:
                if not request.session.session_key:
                    request.session.save()
                key = request.session.session_key or ''
            if key and not request.session.get('visitor_recorded'):
                Visitor.objects.get_or_create(key=key)
                request.session['visitor_recorded'] = True
        response = self.get_response(request)
        return response
