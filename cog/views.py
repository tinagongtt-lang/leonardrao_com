from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect, render

from .engine import Agent, MemoryStore, MockAI

superuser_required = user_passes_test(
    lambda u: u.is_authenticated and u.is_superuser,
    login_url='/accounts/login/',
)


def _agent_for(user) -> Agent:
    return Agent(MockAI(), memory=MemoryStore(user))


@superuser_required
def home(request):
    agent = _agent_for(request.user)

    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        if text == '重置':
            agent.new_session()
            return redirect('cog:home')
        if text:
            events = []
            agent.run(text, trace=events.append)
            request.session['cog_trace'] = events[-8:]
        return redirect('cog:home')

    trace = request.session.pop('cog_trace', [])
    return render(request, 'cog/home.html', {
        'messages': [m for m in agent.messages if m.role != 'system'],
        'session_id': agent.session_id,
        'trace': trace,
    })
