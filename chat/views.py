from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from .models import Message
from .models import Group, GroupMessage, ChatInvite, OfficeProfile
from .models import ChatPresence, StatusUpdate
@login_required


def chat_list(request):
    q = request.GET.get('q', '')

    # 1. Sirf wo log jin se chat hui hai
    chatted_users = User.objects.filter(
        Q(sent_messages__receiver=request.user) |
        Q(received_messages__sender=request.user)
    ).exclude(id=request.user.id).distinct()

    # 2. Sare Groups - ye hamesha show honge
    groups = Group.objects.filter(members=request.user)

    # 3. Search me jo likha ho
    search_results = []
    if q:
        search_results = User.objects.filter(username__icontains=q).exclude(id=request.user.id)

    return render(request, 'chat/chat_list.html', {
        'chatted_users': chatted_users,
        'groups': groups,
        'search_results': search_results,
        'q': q,
    })

@login_required
def updates(request):
    now = timezone.now()
    StatusUpdate.objects.filter(created_at__lte=now - timedelta(hours=24)).delete()
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()[:500]
        media = request.FILES.get('media')
        if text or media:
            StatusUpdate.objects.create(user=request.user, text=text, media=media)
        return redirect('chat_updates')
    statuses = StatusUpdate.objects.select_related('user').filter(created_at__gt=now-timedelta(hours=24)).order_by('-created_at')
    return render(request, 'chat/updates.html', {'statuses': statuses})

@login_required
def chat_room(request, username):
    other_user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        msg = request.POST.get('message', '')
        att = request.FILES.get('attachment')
        if msg.strip() or att:
            Message.objects.create(sender=request.user, receiver=other_user, message=msg, attachment=att)
        presence, _ = ChatPresence.objects.get_or_create(user=request.user)
        presence.save()
        # AJAX se aaya hai to page reload MAT karo, sirf OK bhejo
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('chat_room', username=other_user.username)

    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    return render(request, 'chat/chat_room.html', {'other_user': other_user, 'messages': messages})


from django.http import JsonResponse

@login_required
def get_messages(request, username):
    other_user = get_object_or_404(User, username=username)
    now = timezone.now()
    presence, _ = ChatPresence.objects.get_or_create(user=request.user)
    presence.save()
    Message.objects.filter(sender=other_user, receiver=request.user, read_at__isnull=True).update(read_at=now)
    messages = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) | Q(sender=other_user, receiver=request.user)
    ).order_by('timestamp')
    other_presence = ChatPresence.objects.filter(user=other_user).first()
    online = bool(other_presence and other_presence.last_seen >= now - timedelta(seconds=35))
    typing = bool(other_presence and other_presence.typing_to_id == request.user.id and other_presence.typing_until and other_presence.typing_until >= now)
    data = []
    for m in messages:
            data.append({
                'id': m.id,
                'sender': m.sender.username,
                'message': m.message,
                'timestamp': m.timestamp.strftime('%I:%M %p'),
                'is_me': m.sender == request.user,
                'attachment_url': m.attachment.url if m.attachment else '',
                'is_read': bool(m.read_at),
        })
    return JsonResponse({
        'messages': data,
        'online': online,
        'typing': typing,
        'last_seen': other_presence.last_seen.strftime('%I:%M %p') if other_presence and not online else '',
    })


@login_required
def chat_presence(request, username):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    other_user = get_object_or_404(User, username=username)
    presence, _ = ChatPresence.objects.get_or_create(user=request.user)
    presence.last_seen = timezone.now()
    if request.POST.get('typing') == '1':
        presence.typing_to = other_user
        presence.typing_until = timezone.now() + timedelta(seconds=5)
    else:
        presence.typing_to = None
        presence.typing_until = None
    presence.save()
    return JsonResponse({'status': 'ok'})

  

# ===== GROUP CHAT =====
from .models import Group, GroupMessage

@login_required
def group_list(request):
    groups = Group.objects.filter(members=request.user)
    all_groups = Group.objects.all()
    return render(request, 'chat/group_list.html', {'groups': groups, 'all_groups': all_groups})

@login_required
def create_group(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        group = Group.objects.create(name=name)
        group.members.add(request.user)
        return redirect('group_list')
    return render(request, 'chat/create_group.html')

@login_required
def get_group_messages(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not _can_access_group(request.user, group):
        return JsonResponse({'messages': []}, status=403)
    messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
    data = []
    for m in messages:
        data.append({
            'sender': m.sender.username,
            'message': m.message or '',
            'time': m.timestamp.strftime('%H:%M'),
            'is_me': m.sender == request.user,
            'attachment_url': m.attachment.url if m.attachment else None,
        })
    return JsonResponse({'messages': data})
@login_required
def invite_user(request, username):
    to_user = get_object_or_404(User, username=username)
    # Pehle se invite to nahi bheja hua?
    invite, created = ChatInvite.objects.get_or_create(
        from_user=request.user, to_user=to_user,
        defaults={'is_accepted': False}
    )
    return redirect('/chat/?q=' + username)

@login_required
def accept_invite(request, invite_id):
    invite = get_object_or_404(ChatInvite, id=invite_id, to_user=request.user)
    invite.is_accepted = True
    invite.save()
    # Ab dono ka OfficeProfile ban jayega, matlab dono Office Chat pe aa gaye
    OfficeProfile.objects.get_or_create(user=request.user)
    OfficeProfile.objects.get_or_create(user=invite.from_user)
    return redirect('/chat/')
@login_required
def group_room(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not _can_access_group(request.user, group):
        return redirect('group_list')

    if request.method == 'POST':
        msg = request.POST.get('message', '')
        att = request.FILES.get('attachment')
        if msg.strip() or att:
            GroupMessage.objects.create(
                group=group,
                sender=request.user,
                message=msg,
                attachment=att if att else None
            )
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'ok'})
        return redirect('group_room', group_id=group.id)

    messages = GroupMessage.objects.filter(group=group).order_by('timestamp')
    return render(request, 'chat/group_room.html', {
        'group': group,
        'messages': messages,
    })


def _can_manage_groups(user):
    return user.is_authenticated and user.username == 'razafinal'


def _can_access_group(user, group):
    return _can_manage_groups(user) or group.members.filter(pk=user.pk).exists()


@login_required
def group_details(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if not _can_access_group(request.user, group):
        return redirect('group_list')
    can_manage = _can_manage_groups(request.user)
    if request.method == 'POST' and can_manage:
        action = request.POST.get('action')
        if action == 'update_group':
            group.name = request.POST.get('name', group.name).strip()[:100] or group.name
            group.rules = request.POST.get('rules', '')
            icon = request.FILES.get('icon')
            if icon:
                group.icon = icon
            group.save()
        elif action == 'add_members':
            ids = request.POST.getlist('members')
            group.members.add(*User.objects.filter(id__in=ids))
        elif action == 'remove_member':
            member = get_object_or_404(User, id=request.POST.get('user_id'))
            group.members.remove(member)
        return redirect('group_details', group_id=group.id)
    contacts = User.objects.exclude(pk__in=group.members.values_list('pk', flat=True)).order_by('username')
    return render(request, 'chat/group_details.html', {
        'group': group,
        'can_manage': can_manage,
        'contacts': contacts,
        'members': group.members.order_by('username'),
    })
