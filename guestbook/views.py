from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import MessageForm
from .models import Message


def guestbook(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            msg = form.save(commit=False)
            if request.user.is_authenticated:
                msg.user = request.user
            else:
                if not request.session.session_key:
                    request.session.save()
                msg.session_key = request.session.session_key or ''
            msg.save()
            return redirect('guestbook:guestbook')
    else:
        form = MessageForm()

    paginator = Paginator(Message.objects.order_by('-created_at'), 20)
    page = request.GET.get('page', 1)
    messages = paginator.get_page(page)
    for m in messages:
        m.deletable = m.can_delete(request)
    return render(request, 'guestbook/guestbook.html', {
        'form': form,
        'messages': messages,
    })


@require_POST
def delete_message(request, pk):
    msg = get_object_or_404(Message, pk=pk)
    if msg.can_delete(request):
        msg.delete()
    return redirect('guestbook:guestbook')
