from pathlib import Path

from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.translation import gettext_lazy as _

from .models import FriendlyLink, VisitCounter

BASE_DIR = Path(__file__).resolve().parent.parent


def home(request):
    counter, _ = VisitCounter.objects.get_or_create(name='total', defaults={'count': 0})
    return render(request, 'core/home.html', {'visit_count': counter.count})


def visit_count_api(request):
    counter, _ = VisitCounter.objects.get_or_create(name='total', defaults={'count': 0})
    return JsonResponse({'count': counter.count})


def service_worker(request):
    sw_path = BASE_DIR / 'static' / 'js' / 'service-worker.js'
    with open(sw_path, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='application/javascript')


def links(request):
    if request.method == 'POST' and request.user.is_superuser:
        action = request.POST.get('action')
        if action == 'add':
            name = request.POST.get('name', '').strip()
            url = request.POST.get('url', '').strip()
            if name and url:
                FriendlyLink.objects.create(name=name, url=url)
                messages.success(request, _('链接已添加'))
        elif action == 'delete':
            try:
                pk = int(request.POST.get('pk', 0))
                FriendlyLink.objects.filter(pk=pk).delete()
                messages.success(request, _('链接已删除'))
            except (ValueError, FriendlyLink.DoesNotExist):
                pass
        return redirect('core:links')
    return render(request, 'core/links.html', {
        'links': FriendlyLink.objects.all(),
    })


def robots_txt(request):
    lines = [
        'User-agent: *',
        'Allow: /',
        'Sitemap: /sitemap.xml',
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
