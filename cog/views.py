import re

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
    display = []
    for m in agent.messages:
        if m.role == 'system':
            continue
        kind = 'toolcall' if m.role == 'assistant' and m.content.startswith('Action(') else m.role
        if kind == 'toolcall':
            match = re.search(r"tool='(\w+)'", m.content)
            display.append({'role': kind, 'content': match.group(1) if match else '', 'name': ''})
        else:
            display.append({'role': m.role, 'content': m.content, 'name': m.name})
    return render(request, 'cog/home.html', {
        'messages': display,
        'session_id': agent.session_id,
        'trace': trace,
    })
