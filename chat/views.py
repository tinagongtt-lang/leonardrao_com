import ipaddress
import re
import secrets
import socket
import uuid
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

MAX_IMAGE_SIZE = 20 * 1024 * 1024  # 20M

from .models import ChatProfile, ChatRoom, FriendRequest, RoomInvite, get_profile


def notify_user(user_id):
    layer = get_channel_layer()
    if layer:
        async_to_sync(layer.group_send)(
            f'chat_user_{user_id}', {'type': 'notify'}
        )


def room_broadcast(code, payload):
    layer = get_channel_layer()
    if layer:
        async_to_sync(layer.group_send)(
            f'chat_{code}', dict(payload)
        )


@login_required
def chat_home(request):
    profile = get_profile(request.user)
    return render(request, 'chat/home.html', {
        'profile': profile,
        'rooms': request.user.chat_rooms.all(),
        'friends': profile.friends.all(),
        'friend_requests': request.user.received_friend_requests.filter(status='pending').select_related('from_user'),
        'room_invites': request.user.received_room_invites.filter(status='pending').select_related('from_user', 'room'),
    })


@login_required
@require_POST
def add_friend(request):
    code = request.POST.get('code', '').strip()
    try:
        target = ChatProfile.objects.get(friend_code=code)
    except ChatProfile.DoesNotExist:
        return redirect('chat:home')
    if target.user_id == request.user.id:
        return redirect('chat:home')
    profile = get_profile(request.user)
    if profile.friends.filter(id=target.id).exists():
        return redirect('chat:home')
    exists = FriendRequest.objects.filter(
        from_user=request.user, to_user=target.user, status='pending'
    ).exists() or FriendRequest.objects.filter(
        from_user=target.user, to_user=request.user, status='pending'
    ).exists()
    if not exists:
        FriendRequest.objects.create(from_user=request.user, to_user=target.user)
        notify_user(target.user_id)
    return redirect('chat:home')


@login_required
@require_POST
def friend_request_respond(request, pk, action):
    fr = get_object_or_404(FriendRequest, pk=pk, to_user=request.user, status='pending')
    if action == 'accept':
        fr.status = 'accepted'
        fr.save()
        p_from = get_profile(fr.from_user)
        p_to = get_profile(fr.to_user)
        p_from.friends.add(p_to)
    else:
        fr.status = 'declined'
        fr.save()
    notify_user(fr.from_user_id)
    return redirect('chat:home')


@login_required
@require_POST
def room_create(request):
    name = request.POST.get('name', '').strip() or f'{request.user.username} 的聊天室'
    room = ChatRoom.objects.create(code=secrets.token_hex(4), name=name, owner=request.user)
    room.members.add(request.user)
    return redirect('chat:room', code=room.code)


@login_required
def room_detail(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not room.members.filter(id=request.user.id).exists():
        return redirect('chat:home')
    profile = get_profile(request.user)
    friends = profile.friends.exclude(user_id__in=room.members.values('id'))
    admin_ids = set(room.admins.values_list('id', flat=True))
    members = [
        {
            'user': m,
            'is_owner': m.id == room.owner_id,
            'is_admin': m.id in admin_ids,
            'can_kick': (
                (request.user.id == room.owner_id and m.id != room.owner_id)
                or (request.user.id in admin_ids and m.id != room.owner_id and m.id not in admin_ids)
            ),
            'can_toggle_admin': request.user.id == room.owner_id and m.id != room.owner_id,
        }
        for m in room.members.all()
    ]
    awaiting = []
    if room.is_admin_or_owner(request.user):
        awaiting = room.invites.filter(status='awaiting').select_related('from_user', 'to_user')
    return render(request, 'chat/room.html', {
        'room': room,
        'friends': friends,
        'members': members,
        'awaiting': awaiting,
        'messages': room.messages.select_related('sender')[:100],
        'is_owner': room.owner_id == request.user.id,
        'is_admin': request.user.id in admin_ids,
    })


def _send_invite(request, room, target):
    if target.id == request.user.id or room.members.filter(id=target.id).exists():
        return
    exists = RoomInvite.objects.filter(
        room=room, to_user=target, status__in=('awaiting', 'pending')
    ).exists()
    if exists:
        return
    if room.is_admin_or_owner(request.user):
        RoomInvite.objects.create(room=room, from_user=request.user, to_user=target, status='pending')
        notify_user(target.id)
    else:
        inv = RoomInvite.objects.create(room=room, from_user=request.user, to_user=target, status='awaiting')
        for uid in [room.owner_id, *room.admins.values_list('id', flat=True)]:
            notify_user(uid)


@login_required
@require_POST
def room_add_member(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not room.members.filter(id=request.user.id).exists():
        return redirect('chat:home')
    friend_code = request.POST.get('code', '').strip()
    try:
        target = ChatProfile.objects.get(friend_code=friend_code).user
    except ChatProfile.DoesNotExist:
        return redirect('chat:room', code=room.code)
    _send_invite(request, room, target)
    return redirect('chat:room', code=room.code)


@login_required
@require_POST
def room_add_friend(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not room.members.filter(id=request.user.id).exists():
        return redirect('chat:home')
    try:
        target = User.objects.get(id=int(request.POST.get('user_id', '0')))
    except (User.DoesNotExist, ValueError):
        return redirect('chat:room', code=room.code)
    _send_invite(request, room, target)
    return redirect('chat:room', code=room.code)


@login_required
@require_POST
def invite_approve(request, pk, action):
    invite = get_object_or_404(RoomInvite, pk=pk, status='awaiting')
    if not invite.room.is_admin_or_owner(request.user):
        return redirect('chat:home')
    if action == 'approve':
        invite.status = 'pending'
        invite.save()
        notify_user(invite.to_user_id)
    else:
        invite.status = 'declined'
        invite.save()
        notify_user(invite.from_user_id)
    return redirect('chat:room', code=invite.room.code)


@login_required
@require_POST
def room_invite_respond(request, pk, action):
    invite = get_object_or_404(RoomInvite, pk=pk, to_user=request.user, status='pending')
    if action == 'accept':
        invite.status = 'accepted'
        invite.save()
        invite.room.members.add(request.user)
        return redirect('chat:room', code=invite.room.code)
    invite.status = 'declined'
    invite.save()
    notify_user(invite.from_user_id)
    return redirect('chat:home')


@login_required
@require_POST
def room_upload(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not room.members.filter(id=request.user.id).exists():
        return JsonResponse({'error': 'not a member'}, status=403)
    f = request.FILES.get('image')
    if not f:
        return JsonResponse({'error': 'no file'}, status=400)
    if f.size > MAX_IMAGE_SIZE:
        return JsonResponse({'error': '图片不能超过 20M'}, status=400)
    ctype = getattr(f, 'content_type', '') or ''
    if not ctype.startswith('image/'):
        return JsonResponse({'error': '只能上传图片'}, status=400)
    ext = Path(f.name).suffix.lower() or '.png'
    if ext not in ('.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp', '.svg', '.avif'):
        ext = '.png'
    dest_dir = Path(settings.MEDIA_ROOT) / 'chat' / code
    dest_dir.mkdir(parents=True, exist_ok=True)
    name = f'{uuid.uuid4().hex}{ext}'
    dest = dest_dir / name
    for chunk in f.chunks():
        with open(dest, 'ab') as out:
            out.write(chunk)
    return JsonResponse({'url': f'{settings.MEDIA_URL}chat/{code}/{name}'})


def _is_private_host(hostname):
    # 只拦截 URL 里直接写的内网/保留 IP；域名不查 DNS
    #（本机走 fake-ip 代理，域名解析结果不可靠，且域名访问仍受 HTTP 层约束）
    try:
        ip = ipaddress.ip_address(hostname)
    except ValueError:
        return False
    return ip.is_private or ip.is_loopback or ip.is_reserved or ip.is_link_local or ip.is_multicast


def _meta(html_text, name):
    m = re.search(
        rf'<meta[^>]+(?:property|name)=["\'](?:og:)?{re.escape(name)}["\'][^>]+content=["\']([^"\']+)["\']',
        html_text, re.IGNORECASE)
    if not m:
        m = re.search(
            rf'<meta[^>]+content=["\']([^"\']+)["\'][^>]+(?:property|name)=["\'](?:og:)?{re.escape(name)}["\']',
            html_text, re.IGNORECASE)
    return m.group(1).strip() if m else ''


@login_required
def link_preview(request):
    url = request.GET.get('url', '').strip()
    parsed = urlparse(url)
    if parsed.scheme not in ('http', 'https') or not parsed.hostname or _is_private_host(parsed.hostname):
        return JsonResponse({})
    cache_key = f'linkpreview:{url}'
    cached = cache.get(cache_key)
    if cached is not None:
        return JsonResponse(cached)
    try:
        r = requests.get(
            url, timeout=5, stream=True, allow_redirects=True,
            headers={'User-Agent': 'LeonardRaoLinkPreview/1.0'},
        )
        if not r.ok or 'text/html' not in r.headers.get('Content-Type', ''):
            return JsonResponse({})
        raw = r.raw.read(512 * 1024, decode_content=True)
        html_text = raw.decode(r.encoding or 'utf-8', errors='replace')
        r.close()
    except requests.RequestException:
        return JsonResponse({})
    title = _meta(html_text, 'title')
    if not title:
        m = re.search(r'<title[^>]*>(.*?)</title>', html_text, re.IGNORECASE | re.DOTALL)
        title = re.sub(r'\s+', ' ', m.group(1)).strip() if m else ''
    data = {
        'title': title[:200],
        'description': _meta(html_text, 'description')[:300],
        'image': urljoin(r.url if hasattr(r, 'url') else url, _meta(html_text, 'image')),
        'site': parsed.hostname,
    }
    if not data['title']:
        return JsonResponse({})
    cache.set(cache_key, data, 3600)
    return JsonResponse(data)


@login_required
@require_POST
def room_leave(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    if not room.members.filter(id=request.user.id).exists():
        return redirect('chat:home')
    room.members.remove(request.user)
    room.admins.remove(request.user)
    remaining = list(room.members.all())
    if len(remaining) <= 1:
        room_broadcast(code, {'type': 'room_deleted'})
        room.delete()
    else:
        if room.owner_id == request.user.id:
            admins = room.admins.all()
            room.owner = admins.first() or remaining[0]
            room.save()
            room.admins.remove(room.owner)
    return redirect('chat:home')


@login_required
@require_POST
def room_kick(request, code):
    room = get_object_or_404(ChatRoom, code=code)
    try:
        target = User.objects.get(id=int(request.POST.get('user_id', '0')))
    except (User.DoesNotExist, ValueError):
        return redirect('chat:room', code=room.code)
    is_owner = request.user.id == room.owner_id
    is_admin = room.admins.filter(id=request.user.id).exists()
    target_admin = room.admins.filter(id=target.id).exists()
    if is_owner:
        allowed = target.id != room.owner_id
    elif is_admin:
        allowed = target.id != room.owner_id and not target_admin
    else:
        allowed = False
    if allowed and room.members.filter(id=target.id).exists():
        room.members.remove(target)
        room.admins.remove(target)
        room_broadcast(code, {'type': 'member_kicked', 'user_id': target.id})
        notify_user(target.id)
        if room.members.count() <= 1:
            room_broadcast(code, {'type': 'room_deleted'})
            room.delete()
    return redirect('chat:room', code=room.code) if ChatRoom.objects.filter(code=code).exists() else redirect('chat:home')


@login_required
@require_POST
def room_disband(request, code):
    room = get_object_or_404(ChatRoom, code=code, owner=request.user)
    room_broadcast(code, {'type': 'room_deleted'})
    for uid in room.members.values_list('id', flat=True):
        notify_user(uid)
    room.delete()
    return redirect('chat:home')


@login_required
@require_POST
def room_admin(request, code, action):
    room = get_object_or_404(ChatRoom, code=code, owner=request.user)
    try:
        target = User.objects.get(id=int(request.POST.get('user_id', '0')))
    except (User.DoesNotExist, ValueError):
        return redirect('chat:room', code=room.code)
    if target.id == room.owner_id or not room.members.filter(id=target.id).exists():
        return redirect('chat:room', code=room.code)
    if action == 'add':
        room.admins.add(target)
    else:
        room.admins.remove(target)
    return redirect('chat:room', code=room.code)
