from .models import Visitor


class VisitCounterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.path.startswith(('/admin/', '/static/', '/api/', '/favicon.ico')):
            if request.user.is_authenticated:
                if not request.session.get('visitor_recorded'):
                    Visitor.objects.get_or_create(key=f'u{request.user.pk}')
                    request.session['visitor_recorded'] = True
            elif request.session.session_key:
                # 已带 session cookie 的回访：计为一次独立访客
                if not request.session.get('visitor_recorded'):
                    Visitor.objects.get_or_create(key=request.session.session_key)
                    request.session['visitor_recorded'] = True
            else:
                # 首次访问：种 session cookie，下次带 cookie 回来才算访客
                request.session['visitor_pending'] = True
        response = self.get_response(request)
        return response
