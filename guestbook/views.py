from django.core.paginator import Paginator
from django.shortcuts import redirect, render

from .forms import MessageForm
from .models import Message


def guestbook(request):
    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('guestbook:guestbook')
    else:
        form = MessageForm()

    paginator = Paginator(Message.objects.order_by('-created_at'), 20)
    page = request.GET.get('page', 1)
    messages = paginator.get_page(page)
    return render(request, 'guestbook/guestbook.html', {
        'form': form,
        'messages': messages,
    })
