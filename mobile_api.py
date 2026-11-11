"""Authenticated JSON/multipart API for Campus Times Flutter clients."""
import hashlib, json, secrets, logging
from datetime import timedelta
from functools import wraps
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.core.validators import validate_email
from django.http import JsonResponse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db.models import Q, Count
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import uuid
from chat.models import (Message, MobileAPIToken, Group, GroupMessage, GroupMessageReceipt,
                         ChatPresence, StatusUpdate, StatusView, SocialNotification)
from home.models import Meep, Comment, Profile, Complaint, Video, PostReceipt

MAX_UPLOAD = 25 * 1024 * 1024
logger = logging.getLogger(__name__)

def api_login_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        auth = request.headers.get('Authorization', '')
        if auth.startswith('Bearer '):
            raw = auth[7:].strip()
            digest = hashlib.sha256(raw.encode()).hexdigest()
            token = MobileAPIToken.objects.select_related('user').filter(token_hash=digest).first()
            if token:
                request.user = token.user
        if not getattr(request, 'user', None) or not request.user.is_authenticated:
            return JsonResponse({'error': 'Your session expired. Please sign in again.'}, status=401)
        # Keep last-seen current throughout the signed-in app, not only while
        # a user happens to have a conversation open.
        ChatPresence.objects.update_or_create(
            user=request.user,
            defaults={'last_seen': timezone.now()},
        )
        return view(request, *args, **kwargs)
    return wrapped

def payload(request):
    if request.content_type and request.content_type.startswith('multipart/'):
        return request.POST
    try: return json.loads(request.body or '{}')
    except (ValueError, UnicodeDecodeError): return None

def media_url(request, field, resource_type=None):
    try:
        if not field:
            return ''
        storage = field.storage
        url = (
            storage.url_for_resource_type(field.name, resource_type)
            if resource_type and hasattr(storage, 'url_for_resource_type')
            else field.url
        )
        return request.build_absolute_uri(url) if request else url
    except Exception:
        logger.exception('Could not build a media URL for a stored upload.')
        return ''

def media_name(field):
    """Return a useful original-style filename after Cloudinary storage."""
    if not field:
        return ''
    name = str(field.name or '')
    extension = ''
    if '::' in name:
        metadata, name = name.split('::', 1)
        if '|' in metadata:
            extension = metadata.split('|', 1)[1].lower()
    if not extension:
        from pathlib import Path
        extension = Path(name).suffix.lower()
    basename = name.rsplit('/', 1)[-1]
    if extension and not basename.lower().endswith(extension):
        basename += extension
    # Older voice-note uploads lost their suffix when Cloudinary returned only
    # a public ID. Preserve their audio classification for the mobile player.
    if not extension and basename.lower().startswith('voice_'):
        basename += '.m4a'
    return basename

def notify(recipient, actor, kind, text, target=''):
    if recipient.pk != actor.pk:
        SocialNotification.objects.create(recipient=recipient, actor=actor, kind=kind, text=text, target_url=target)

def emit(group, event_type, payload):
    try:
        async_to_sync(get_channel_layer().group_send)(group, {'type': event_type, 'payload': payload})
    except Exception:
        logger.exception('WebSocket event could not be published.')

def parse_client_id(value):
    try:
        return uuid.UUID(str(value)) if value else None
    except (ValueError, TypeError, AttributeError):
        return None

def user_data(user, request=None):
    profile = Profile.objects.filter(user=user).first()
    return {'id': user.id, 'username': user.username, 'first_name': user.first_name,
            'last_name': user.last_name, 'full_name': user.get_full_name() or user.username,
            'bio': profile.profile_bio if profile else '',
            'home_address': profile.home_address if profile else '',
            'relationship_status': profile.relationship_status if profile else '',
            'education_status': profile.education_status if profile else '',
            'avatar': media_url(request, profile.profile_image) if request and profile and profile.profile_image else '',
            'is_staff': user.is_staff,
            'last_seen_privacy': profile.last_seen_privacy if profile else 'everyone',
            'status_privacy': profile.status_privacy if profile else 'everyone',
            'read_receipts': profile.read_receipts if profile else True}

def post_data(post, request, viewer):
    receipts = list(post.receipts.all())
    own_receipts = [r for r in receipts if r.user_id == viewer.pk]
    return {'id': post.id, 'username': post.user.username, 'user_id': post.user_id,
            'author': user_data(post.user, request), 'title': post.title or '',
            'body': strip_tags(post.body or ''), 'category': post.category or 'General',
            'created_at': post.created_at.isoformat(), 'likes': post.likes.count(),
            'liked': post.likes.filter(pk=viewer.pk).exists(),
            'attachment': media_url(request, post.attachment),
            'attachment_name': media_name(post.attachment),
            'comments_count': post.comments.count(), 'is_mine': post.user_id == viewer.pk,
            'edited_at': post.edited_at.isoformat() if post.edited_at else '',
            'delivered_count': sum(1 for r in receipts if r.delivered_at) if post.user_id == viewer.pk else None,
            'seen_count': sum(1 for r in receipts if r.seen_at) if post.user_id == viewer.pk else None,
            'is_delivered': bool(own_receipts and own_receipts[0].delivered_at) if post.user_id != viewer.pk else False,
            'is_seen': bool(own_receipts and own_receipts[0].seen_at) if post.user_id != viewer.pk else False}

def message_data(m, request, viewer):
    other = m.receiver if m.sender_id == viewer.pk else m.sender
    other_profile = Profile.objects.filter(user=other).first()
    show_read = bool(other_profile is None or other_profile.read_receipts)
    return {'id': m.id, 'sender': m.sender.username, 'sender_id': m.sender_id, 'sender_avatar': user_data(m.sender, request)['avatar'],
            'message': ('This message was deleted' if m.is_deleted else (m.message or '')), 'timestamp': m.timestamp.isoformat(),
            'is_me': m.sender_id == viewer.pk, 'is_read': bool(m.read_at and m.sender_id == viewer.pk and show_read), 'is_delivered': bool(m.delivered_at and m.sender_id == viewer.pk),
            'edited_at': m.edited_at.isoformat() if m.edited_at else '', 'reply_to_id': m.reply_to_id,
            'reply_to': m.reply_to.message if m.reply_to and not m.reply_to.is_deleted else '',
            'attachment': media_url(request, m.attachment), 'attachment_name': media_name(m.attachment)}

@csrf_exempt
@require_http_methods(['POST'])
def mobile_signup(request):
    data = payload(request)
    if not isinstance(data, dict):
        return JsonResponse({'error': 'Invalid registration data.'}, status=400)
    username = str(data.get('username', '')).strip()
    email = str(data.get('email', '')).strip().lower()
    first_name = str(data.get('first_name', '')).strip()
    last_name = str(data.get('last_name', '')).strip()
    password = data.get('password', '')
    confirmation = data.get('confirm_password', '')
    if not username or len(username) > 150:
        return JsonResponse({'error': 'Enter a valid username (up to 150 characters).'}, status=400)
    from django.contrib.auth.validators import UnicodeUsernameValidator
    try:
        UnicodeUsernameValidator()(username)
        validate_email(email)
    except ValidationError as exc:
        return JsonResponse({'error': '; '.join(exc.messages)}, status=400)
    if not isinstance(password, str) or password != confirmation:
        return JsonResponse({'error': 'Passwords do not match.'}, status=400)
    if User.objects.filter(username__iexact=username).exists():
        return JsonResponse({'error': 'This username is already taken.'}, status=409)
    if User.objects.filter(email__iexact=email).exists():
        return JsonResponse({'error': 'This email address is already registered.'}, status=409)
    provisional = User(username=username, email=email, first_name=first_name[:150], last_name=last_name[:150])
    try:
        validate_password(password, user=provisional)
    except ValidationError as exc:
        return JsonResponse({'error': ' '.join(exc.messages)}, status=400)
    try:
        with transaction.atomic():
            user = User.objects.create_user(username=username, email=email, password=password,
                                            first_name=first_name[:150], last_name=last_name[:150])
            Profile.objects.get_or_create(user=user)
    except IntegrityError:
        return JsonResponse({'error': 'Account already exists. Try another username.'}, status=409)
    raw = secrets.token_urlsafe(48)
    MobileAPIToken.objects.create(user=user, token_hash=hashlib.sha256(raw.encode()).hexdigest())
    return JsonResponse({'token': raw, 'user': user_data(user, request), 'username': user.username}, status=201)

@csrf_exempt
@require_http_methods(['POST'])
def mobile_login(request):
    data = payload(request) or {}
    user = authenticate(request, username=data.get('username', ''), password=data.get('password', ''))
    if not user: return JsonResponse({'error': 'Username or password is incorrect.'}, status=401)
    raw = secrets.token_urlsafe(48)
    MobileAPIToken.objects.create(user=user, token_hash=hashlib.sha256(raw.encode()).hexdigest())
    return JsonResponse({'token': raw, 'user': user_data(user, request), 'username': user.username})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','DELETE','PATCH'])
def mobile_me(request):
    if request.method == 'DELETE':
        raw = request.headers.get('Authorization','')[7:]
        MobileAPIToken.objects.filter(user=request.user, token_hash=hashlib.sha256(raw.encode()).hexdigest()).delete()
        return JsonResponse({'ok': True})
    if request.method == 'PATCH':
        data = payload(request) or {}
        request.user.first_name = str(data.get('first_name', request.user.first_name))[:150]
        request.user.last_name = str(data.get('last_name', request.user.last_name))[:150]
        request.user.save(update_fields=['first_name','last_name'])
        profile, _ = Profile.objects.get_or_create(user=request.user)
        profile.profile_bio = str(data.get('bio', profile.profile_bio or ''))[:500]
        profile.last_seen_privacy = data.get('last_seen_privacy', profile.last_seen_privacy) if data.get('last_seen_privacy', profile.last_seen_privacy) in {'everyone','followers','nobody'} else profile.last_seen_privacy
        profile.status_privacy = data.get('status_privacy', profile.status_privacy) if data.get('status_privacy', profile.status_privacy) in {'everyone','followers','nobody'} else profile.status_privacy
        if 'read_receipts' in data: profile.read_receipts = str(data.get('read_receipts')).lower() in ('1','true','yes')
        if request.FILES.get('avatar'): profile.profile_image = request.FILES['avatar']
        profile.save()
    return JsonResponse({'user': user_data(request.user, request)})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_feed(request):
    if request.method == 'POST':
        data = payload(request) or {}
        body = str(data.get('body','')).strip()
        file = request.FILES.get('attachment')
        if not body and not file: return JsonResponse({'error':'Write something or attach a file.'}, status=400)
        if file and file.size > MAX_UPLOAD: return JsonResponse({'error':'Maximum upload size is 25 MB.'}, status=413)
        client_id = parse_client_id(data.get('client_id'))
        defaults={'body':body,'title':str(data.get('title','Campus update'))[:255],'category':str(data.get('category','General'))[:255],'attachment':file}
        if client_id: post,created=Meep.objects.get_or_create(user=request.user,client_id=client_id,defaults=defaults)
        else: post,created=Meep.objects.create(user=request.user,**defaults),True
        payload_data = post_data(post, request, request.user)
        if created:
            emit('campus_feed', 'post.event', payload_data)
        return JsonResponse({'post':payload_data}, status=201 if created else 200)
    qs = Meep.objects.select_related('user').prefetch_related('likes','receipts','comments').order_by('-created_at')[:100]
    now = timezone.now()
    for post in qs:
        if post.user_id != request.user.pk:
            _,created=PostReceipt.objects.get_or_create(post=post, user=request.user, defaults={'delivered_at': now})
            if created: emit('campus_feed','receipt.event',{'type':'post.receipt','post_id':post.pk,'user_id':request.user.pk,'delivered':True})
            getattr(post, '_prefetched_objects_cache', {}).pop('receipts', None)
    return JsonResponse({'posts':[post_data(p, request, request.user) for p in qs]})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_post_seen(request, post_id):
    post = Meep.objects.filter(pk=post_id).first()
    if not post:
        return JsonResponse({'error':'Post not found.'}, status=404)
    if post.user_id != request.user.pk:
        receipt, _ = PostReceipt.objects.get_or_create(post=post, user=request.user)
        now = timezone.now()
        changed = not bool(receipt.seen_at)
        if not receipt.seen_at:
            receipt.delivered_at = receipt.delivered_at or now
            receipt.seen_at = now
            receipt.save(update_fields=['delivered_at','seen_at'])
        if changed: emit('campus_feed', 'receipt.event', {'type':'post.receipt','post_id':post.pk,'user_id':request.user.pk,'seen':True})
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['PATCH','DELETE'])
def mobile_post_detail(request, post_id):
    post = Meep.objects.filter(pk=post_id).first()
    if not post: return JsonResponse({'error':'Post not found.'}, status=404)
    if post.user_id != request.user.pk: return JsonResponse({'error':'You can only edit or delete your own post.'}, status=403)
    if request.method == 'DELETE':
        if post.attachment: post.attachment.delete(save=False)
        post.delete()
        return JsonResponse({'ok':True})
    data = payload(request) or {}
    if 'body' in data: post.body = str(data.get('body','')).strip()
    if 'title' in data: post.title = str(data.get('title','')).strip()[:255]
    attachment = request.FILES.get('attachment')
    if attachment:
        if attachment.size > MAX_UPLOAD: return JsonResponse({'error':'Maximum upload size is 25 MB.'}, status=413)
        post.attachment = attachment
    post.edited_at = timezone.now()
    post.save()
    return JsonResponse({'post':post_data(post,request,request.user)})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_like(request, post_id):
    post = Meep.objects.select_related('user').filter(pk=post_id).first()
    if not post: return JsonResponse({'error':'Post not found.'}, status=404)
    if post.likes.filter(pk=request.user.pk).exists(): post.likes.remove(request.user)
    else:
        post.likes.add(request.user); notify(post.user, request.user, 'like', f'{request.user.username} liked your post', f'/post/{post.id}')
    return JsonResponse({'liked':post.likes.filter(pk=request.user.pk).exists(), 'likes':post.likes.count()})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_comments(request, post_id):
    post = Meep.objects.filter(pk=post_id).first()
    if not post: return JsonResponse({'error':'Post not found.'}, status=404)
    if request.method == 'POST':
        data = payload(request) or {}; body = str(data.get('body','')).strip()
        if not body: return JsonResponse({'error':'Comment cannot be empty.'}, status=400)
        parent = None
        if data.get('parent_id'):
            parent = Comment.objects.filter(pk=data.get('parent_id'), post=post).first()
            if not parent: return JsonResponse({'error':'Reply target not found.'}, status=404)
        comment = Comment.objects.create(post=post, user=request.user, parent=parent, name=request.user.username, body=body[:5000])
        notify(post.user, request.user, 'comment', f'{request.user.username} commented on your post', f'/post/{post.id}')
        if parent and parent.user_id and parent.user_id != request.user.pk:
            notify(parent.user, request.user, 'comment', f'{request.user.username} replied to your comment', f'/post/{post.id}')
        return JsonResponse({'comment':comment_data(comment,request)}, status=201)
    return JsonResponse({'comments':[comment_data(c,request) for c in post.comments.select_related('user','parent').order_by('date_added','id')]})

def comment_data(comment, request):
    return {'id':comment.id,'username':comment.name,'user_id':comment.user_id,'body':comment.body,
            'created_at':comment.date_added.isoformat(),'parent_id':comment.parent_id,
            'parent_username':comment.parent.name if comment.parent else '',
            'is_mine':comment.user_id == request.user.pk}

@csrf_exempt
@api_login_required
@require_http_methods(['PATCH','DELETE'])
def mobile_comment_detail(request, post_id, comment_id):
    comment=Comment.objects.filter(pk=comment_id,post_id=post_id).first()
    if not comment:return JsonResponse({'error':'Comment not found.'},status=404)
    if comment.user_id != request.user.pk and comment.post.user_id != request.user.pk:
        return JsonResponse({'error':'Only the comment author or post owner can remove it.'},status=403)
    if request.method=='DELETE':
        comment.delete(); return JsonResponse({'ok':True})
    if comment.user_id != request.user.pk:return JsonResponse({'error':'You can only edit your own comment.'},status=403)
    data=payload(request) or {}; body=str(data.get('body','')).strip()
    if not body:return JsonResponse({'error':'Comment cannot be empty.'},status=400)
    comment.body=body[:5000]; comment.save(update_fields=['body','updated_at'])
    return JsonResponse({'comment':comment_data(comment,request)})

@csrf_exempt
@api_login_required
@require_http_methods(['GET'])
def mobile_contacts(request):
    q = request.GET.get('q','').strip()
    users = User.objects.exclude(pk=request.user.pk).filter(is_active=True)
    if q: users = users.filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q))
    result=[]
    for person in users.order_by('username')[:150]:
        last=Message.objects.filter(Q(sender=request.user,receiver=person)|Q(sender=person,receiver=request.user)).exclude(hidden_for=request.user).order_by('-timestamp').first()
        unread=Message.objects.filter(sender=person,receiver=request.user,read_at__isnull=True).exclude(hidden_for=request.user).count()
        presence=ChatPresence.objects.filter(user=person).first()
        target_profile=Profile.objects.filter(user=person).first()
        can_see=(not target_profile or target_profile.last_seen_privacy=='everyone' or (target_profile.last_seen_privacy=='followers' and Profile.objects.filter(user=person,followed_by__user=request.user).exists()))
        result.append({**user_data(person,request),'last_message':(last.message if last else '') or ('Attachment' if last and last.attachment else ''), 'last_message_at':last.timestamp.isoformat() if last else '', 'unread':unread,'online':bool(can_see and presence and presence.last_seen >= timezone.now()-timedelta(seconds=45))})
    return JsonResponse({'people':result})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_chat(request, username):
    other=User.objects.filter(username=username,is_active=True).first()
    if not other: return JsonResponse({'error':'Person not found.'},status=404)
    if other.pk == request.user.pk: return JsonResponse({'error':'You cannot message yourself.'},status=400)
    if request.method == 'POST':
        data=payload(request) or {}; text=str(data.get('message','')).strip(); file=request.FILES.get('attachment')
        if not text and not file: return JsonResponse({'error':'Write a message or attach a file.'},status=400)
        if file and file.size>MAX_UPLOAD: return JsonResponse({'error':'Maximum upload size is 25 MB.'},status=413)
        reply_to=Message.objects.filter(pk=data.get('reply_to_id'),sender__in=[request.user,other],receiver__in=[request.user,other]).first() if data.get('reply_to_id') else None
        client_id=parse_client_id(data.get('client_id'))
        if client_id: sent,created=Message.objects.get_or_create(sender=request.user,client_id=client_id,defaults={'receiver':other,'message':text,'attachment':file,'reply_to':reply_to})
        else: sent,created=Message.objects.create(sender=request.user,receiver=other,message=text,attachment=file,reply_to=reply_to),True
        if sent.receiver_id != other.pk: return JsonResponse({'error':'Client message ID already belongs to another conversation.'},status=409)
        if created:
            notify(other,request.user,'message',f'New message from {request.user.username}',f'/chat/{request.user.username}')
            event={'kind':'direct','id':sent.pk,'client_id':str(client_id or ''),'sender':request.user.username,'sender_id':request.user.pk,'recipient':other.username,'message':sent.message or '', 'timestamp':sent.timestamp.isoformat(),'is_delivered':False}
            emit(f'user_{other.pk}','chat.event',event)
            emit(f'user_{request.user.pk}','chat.event',event)
        return JsonResponse({'message':message_data(sent,request,request.user)},status=201 if created else 200)
    now=timezone.now()
    viewer_profile,_=Profile.objects.get_or_create(user=request.user)
    if viewer_profile.read_receipts:
        seen_ids=list(Message.objects.filter(sender=other,receiver=request.user,read_at__isnull=True).values_list('id',flat=True))
        Message.objects.filter(id__in=seen_ids).update(read_at=now)
        if seen_ids: emit(f'user_{other.pk}','receipt.event',{'type':'message.seen','message_ids':seen_ids,'reader_id':request.user.pk})
    delivered_ids=list(Message.objects.filter(sender=other,receiver=request.user,delivered_at__isnull=True).values_list('id',flat=True))
    Message.objects.filter(id__in=delivered_ids).update(delivered_at=now)
    if delivered_ids: emit(f'user_{other.pk}','receipt.event',{'type':'message.delivered','message_ids':delivered_ids,'recipient_id':request.user.pk})
    ChatPresence.objects.update_or_create(user=request.user,defaults={'last_seen':now})
    qs=Message.objects.filter(Q(sender=request.user,receiver=other)|Q(sender=other,receiver=request.user)).exclude(hidden_for=request.user).select_related('sender','receiver','reply_to').order_by('-timestamp','-id')[:300]
    msgs=[message_data(m,request,request.user) for m in list(qs)[::-1]]
    p=ChatPresence.objects.filter(user=other).first()
    other_profile=Profile.objects.filter(user=other).first()
    can_see_presence=(not other_profile or other_profile.last_seen_privacy=='everyone' or (other_profile.last_seen_privacy=='followers' and Profile.objects.filter(user=other,followed_by__user=request.user).exists()))
    online=bool(can_see_presence and p and p.last_seen>=now-timedelta(seconds=45))
    typing=bool(p and p.typing_to_id==request.user.id and p.typing_until and p.typing_until>=now)
    return JsonResponse({'person':user_data(other,request),'messages':msgs,'online':online,'typing':typing and can_see_presence,'last_seen':p.last_seen.isoformat() if p and not online and can_see_presence else ''})

@csrf_exempt
@api_login_required
@require_http_methods(['PATCH','DELETE'])
def mobile_message_detail(request, username, message_id):
    other=User.objects.filter(username=username,is_active=True).first()
    message=Message.objects.filter(pk=message_id,sender=request.user,receiver=other).first() if other else None
    if not message:return JsonResponse({'error':'Message not found or not yours to edit.'},status=404)
    if request.method=='DELETE':
        if message.attachment: message.attachment.delete(save=False)
        message.message=''; message.is_deleted=True; message.save(update_fields=['message','is_deleted'])
        return JsonResponse({'ok':True})
    data=payload(request) or {}; message.message=str(data.get('message','')).strip()
    if not message.message and not message.attachment:return JsonResponse({'error':'A message cannot be empty.'},status=400)
    message.edited_at=timezone.now(); message.save(update_fields=['message','edited_at'])
    return JsonResponse({'message':message_data(message,request,request.user)})

@csrf_exempt
@api_login_required
@require_http_methods(['DELETE'])
def mobile_clear_chat(request, username):
    other=User.objects.filter(username=username,is_active=True).first()
    if not other:return JsonResponse({'error':'Person not found.'},status=404)
    for message in Message.objects.filter(Q(sender=request.user,receiver=other)|Q(sender=other,receiver=request.user)).exclude(hidden_for=request.user):
        message.hidden_for.add(request.user)
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['PATCH','DELETE'])
def mobile_group_message_detail(request, group_id, message_id):
    group=Group.objects.filter(pk=group_id,members=request.user).first()
    message=GroupMessage.objects.filter(pk=message_id,group=group,sender=request.user).first() if group else None
    if not message:return JsonResponse({'error':'Message not found or not yours to edit.'},status=404)
    if request.method=='DELETE':
        if message.attachment: message.attachment.delete(save=False)
        message.message=''; message.is_deleted=True; message.save(update_fields=['message','is_deleted'])
        return JsonResponse({'ok':True})
    data=payload(request) or {}; message.message=str(data.get('message','')).strip()
    if not message.message and not message.attachment:return JsonResponse({'error':'A message cannot be empty.'},status=400)
    message.edited_at=timezone.now(); message.save(update_fields=['message','edited_at'])
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['DELETE'])
def mobile_group_leave(request, group_id):
    group=Group.objects.filter(pk=group_id,members=request.user).first()
    if not group:return JsonResponse({'error':'Group not found.'},status=404)
    remaining=list(group.members.exclude(pk=request.user.pk).order_by('id'))
    if group.admin_id==request.user.pk and remaining:
        group.admin=remaining[0]; group.save(update_fields=['admin'])
    group.members.remove(request.user)
    if not remaining: group.delete()
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_group_promote(request, group_id):
    group=Group.objects.filter(pk=group_id,members=request.user).first()
    if not group:return JsonResponse({'error':'Group not found.'},status=404)
    if group.admin_id!=request.user.pk:return JsonResponse({'error':'Only the group admin can promote members.'},status=403)
    target_id=(payload(request) or {}).get('user_id')
    target=User.objects.filter(pk=target_id,chat_groups=group).first()
    if not target:return JsonResponse({'error':'Member not found.'},status=404)
    # The current schema supports one admin; the original admin stays in charge.
    group.admin=target; group.save(update_fields=['admin'])
    return JsonResponse({'group':group_data(group,request.user)})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_presence(request, username):
    other=User.objects.filter(username=username).first()
    data=payload(request) or {}
    presence,_=ChatPresence.objects.get_or_create(user=request.user)
    presence.last_seen=timezone.now()
    presence.typing_to=other if data.get('typing') and other else None
    presence.typing_until=timezone.now()+timedelta(seconds=6) if presence.typing_to else None
    presence.save()
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_groups(request):
    if request.method=='POST':
        data=payload(request) or {}; name=str(data.get('name','')).strip()[:100]
        if not name:return JsonResponse({'error':'Group name is required.'},status=400)
        group=Group.objects.create(name=name,admin=request.user); group.members.add(request.user)
        ids=data.get('member_ids',[])
        if isinstance(ids,list): group.members.add(*User.objects.filter(id__in=ids,is_active=True))
        return JsonResponse({'group':group_data(group,request.user)},status=201)
    groups=Group.objects.filter(members=request.user).annotate(member_count=Count('members')).order_by('-created_at')
    return JsonResponse({'groups':[group_data(g,request.user) for g in groups]})

def group_data(group,user):
    last=group.messages.order_by('-timestamp').first()
    return {'id':group.id,'name':group.name,'icon':media_url(None,group.icon),'admin_id':group.admin_id,'is_admin':group.admin_id==user.pk,'member_count':group.members.count(),'last_message':(last.message or 'Attachment') if last else '', 'last_message_at':last.timestamp.isoformat() if last else ''}

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_group_chat(request, group_id):
    group=Group.objects.filter(pk=group_id,members=request.user).first()
    if not group:return JsonResponse({'error':'Group not found or access denied.'},status=404)
    if request.method=='POST':
        data=payload(request) or {}; text=str(data.get('message','')).strip(); file=request.FILES.get('attachment')
        if not text and not file:return JsonResponse({'error':'Write a message or attach a file.'},status=400)
        if file and file.size>MAX_UPLOAD:return JsonResponse({'error':'Maximum upload size is 25 MB.'},status=413)
        reply_to=GroupMessage.objects.filter(pk=data.get('reply_to_id'),group=group).first() if data.get('reply_to_id') else None
        client_id=parse_client_id(data.get('client_id'))
        if client_id: msg,created=GroupMessage.objects.get_or_create(group=group,sender=request.user,client_id=client_id,defaults={'message':text,'attachment':file,'reply_to':reply_to})
        else: msg,created=GroupMessage.objects.create(group=group,sender=request.user,message=text,attachment=file,reply_to=reply_to),True
        if msg.group_id != group.pk:return JsonResponse({'error':'Client message ID already belongs to another group.'},status=409)
        if created:
            now=timezone.now()
            for member in group.members.exclude(pk=request.user.pk): GroupMessageReceipt.objects.get_or_create(message=msg,user=member,defaults={'delivered_at':None})
            emit(f'chat_group_{group.pk}','chat.event',{'kind':'group','group_id':group.pk,'id':msg.pk,'client_id':str(client_id or ''),'sender':request.user.username,'sender_id':request.user.pk,'message':msg.message or '', 'timestamp':msg.timestamp.isoformat()})
        if created:
            for member in group.members.exclude(pk=request.user.pk): notify(member,request.user,'group',f'New message in {group.name}',f'/groups/{group.id}')
        return JsonResponse({'message':{'id':msg.id,'sender':msg.sender.username,'sender_id':msg.sender_id,'message':msg.message or '', 'timestamp':msg.timestamp.isoformat(),'is_me':True,'attachment':media_url(request,msg.attachment),'attachment_name':media_name(msg.attachment),'client_id':str(client_id or '')}},status=201 if created else 200)
    now=timezone.now()
    delivered_any=False
    with transaction.atomic():
        recent_ids=list(group.messages.order_by('-timestamp').values_list('id',flat=True)[:300])
        for msg in group.messages.filter(id__in=recent_ids).exclude(sender=request.user):
            receipt,_=GroupMessageReceipt.objects.get_or_create(message=msg,user=request.user)
            if not receipt.delivered_at:
                receipt.delivered_at=now
                receipt.save(update_fields=['delivered_at'])
                delivered_any=True
    if delivered_any: emit(f'chat_group_{group.pk}','receipt.event',{'type':'group.receipt','group_id':group.pk,'user_id':request.user.pk,'delivered':True})
    qs=group.messages.select_related('sender','reply_to').prefetch_related('receipts').order_by('-timestamp')[:300]
    data=[]
    for m in list(qs)[::-1]:
        receipt_rows=list(m.receipts.all())
        data.append({'id':m.id,'sender':m.sender.username,'sender_id':m.sender_id,'message':'This message was deleted' if m.is_deleted else (m.message or ''), 'timestamp':m.timestamp.isoformat(),'is_me':m.sender_id==request.user.pk,'attachment':media_url(request,m.attachment),'attachment_name':media_name(m.attachment), 'edited_at':m.edited_at.isoformat() if m.edited_at else '', 'reply_to_id':m.reply_to_id,'reply_to':m.reply_to.message if m.reply_to and not m.reply_to.is_deleted else '', 'client_id':str(m.client_id or ''),'is_delivered':any(r.delivered_at for r in receipt_rows),'is_read':any(r.seen_at for r in receipt_rows)})
    return JsonResponse({'group':group_data(group,request.user),'members':[user_data(u,request) for u in group.members.all()],'messages':data})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_group_members(request, group_id):
    group=Group.objects.filter(pk=group_id,members=request.user).first()
    if not group:return JsonResponse({'error':'Group not found.'},status=404)
    data=payload(request) or {}; ids=data.get('member_ids',[])
    if not isinstance(ids,list):return JsonResponse({'error':'member_ids must be a list.'},status=400)
    if group.admin_id != request.user.pk:return JsonResponse({'error':'Only a group admin can add members.'},status=403)
    group.members.add(*User.objects.filter(id__in=ids,is_active=True))
    return JsonResponse({'group':group_data(group,request.user)})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_notifications(request):
    if request.method=='POST':
        SocialNotification.objects.filter(recipient=request.user,is_read=False).update(is_read=True)
        return JsonResponse({'ok':True})
    qs=SocialNotification.objects.filter(recipient=request.user).select_related('actor')[:100]
    return JsonResponse({'unread':SocialNotification.objects.filter(recipient=request.user,is_read=False).count(),'notifications':[{'id':n.id,'kind':n.kind,'text':n.text,'actor':n.actor.username,'created_at':n.created_at.isoformat(),'is_read':n.is_read,'target_url':n.target_url} for n in qs]})

def status_data(status, request):
    own = status.user_id == request.user.id
    views = status.views.select_related('user')
    return {'id': status.id, 'username': status.user.username,
            'avatar': user_data(status.user, request)['avatar'],
            'text': status.text, 'media': media_url(request, status.media),
            'media_name': media_name(status.media),
            'created_at': status.created_at.isoformat(), 'expires_at': status.expires_at.isoformat(),
            'is_mine': own, 'viewed': own or views.filter(user=request.user).exists(),
            'view_count': views.count() if own else None,
            'viewers': [{'username': v.user.username, 'viewed_at': v.viewed_at.isoformat()} for v in views] if own else []}

def status_visible_to(status, viewer):
    if status.user_id == viewer.pk: return True
    profile=Profile.objects.filter(user=status.user).first()
    privacy=profile.status_privacy if profile else 'everyone'
    return privacy=='everyone' or (privacy=='followers' and Profile.objects.filter(user=status.user,followed_by__user=viewer).exists())

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_status(request):
    now = timezone.now()
    if request.method == 'POST':
        data = payload(request) or {}
        text = str(data.get('text', '')).strip()[:500]
        file = request.FILES.get('media')
        if not text and not file:
            return JsonResponse({'error': 'Add text, a photo or a video.'}, status=400)
        if file and file.size > MAX_UPLOAD:
            return JsonResponse({'error': 'Status media must be 25 MB or smaller.'}, status=413)
        if file:
            from pathlib import Path
            if Path(file.name).suffix.lower() not in {'.jpg','.jpeg','.png','.webp','.gif','.mp4','.mov','.webm','.m4v'}:
                return JsonResponse({'error': 'Choose a photo or video for your status.'}, status=400)
        st = StatusUpdate.objects.create(user=request.user, text=text, media=file)
        return JsonResponse({'status': status_data(st, request)}, status=201)
    statuses = StatusUpdate.objects.filter(created_at__gt=now-timedelta(hours=24)).select_related('user').order_by('created_at')
    visible=[status for status in statuses if status_visible_to(status,request.user)]
    return JsonResponse({'statuses': [status_data(s, request) for s in visible]})

@csrf_exempt
@api_login_required
@require_http_methods(['POST','DELETE'])
def mobile_status_detail(request, status_id):
    status = StatusUpdate.objects.filter(pk=status_id, created_at__gt=timezone.now()-timedelta(hours=24)).first()
    if not status:
        return JsonResponse({'error': 'This status has expired or was deleted.'}, status=404)
    if request.method == 'DELETE':
        if status.user_id != request.user.id:
            return JsonResponse({'error': 'You can only delete your own status.'}, status=403)
        status.media.delete(save=False)
        status.delete()
        return JsonResponse({'ok': True})
    if not status_visible_to(status,request.user):
        return JsonResponse({'error':'This status is private.'},status=404)
    if status.user_id != request.user.id:
        StatusView.objects.get_or_create(status=status, user=request.user)
    return JsonResponse({'status': status_data(status, request)})

@csrf_exempt
@api_login_required
@require_http_methods(['GET'])
def mobile_search(request):
    q=request.GET.get('q','').strip()
    if not q:return JsonResponse({'people':[],'posts':[]})
    people=User.objects.filter(is_active=True).filter(Q(username__icontains=q)|Q(first_name__icontains=q)|Q(last_name__icontains=q)).exclude(pk=request.user.pk)[:30]
    posts=Meep.objects.filter(Q(title__icontains=q)|Q(body__icontains=q)).select_related('user').order_by('-created_at')[:30]
    return JsonResponse({'people':[user_data(u,request) for u in people],'posts':[post_data(p,request,request.user) for p in posts]})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_profile(request, username):
    person=User.objects.filter(username=username,is_active=True).first()
    if not person:return JsonResponse({'error':'User not found.'},status=404)
    profile,_=Profile.objects.get_or_create(user=person)
    viewer_profile,_=Profile.objects.get_or_create(user=request.user)
    if request.method=='POST':
        data=payload(request) or {}
        if person.pk != request.user.pk:return JsonResponse({'error':'You can only edit your own profile.'},status=403)
        if 'username' in data:
            username=str(data.get('username','')).strip()
            if not username or len(username)>150:
                return JsonResponse({'error':'Enter a username up to 150 characters.'},status=400)
            from django.contrib.auth.validators import UnicodeUsernameValidator
            try:
                UnicodeUsernameValidator()(username)
            except ValidationError as exc:
                return JsonResponse({'error':'; '.join(exc.messages)},status=400)
            if User.objects.exclude(pk=person.pk).filter(username__iexact=username).exists():
                return JsonResponse({'error':'That username is already in use.'},status=409)
            person.username=username
        if 'first_name' in data: person.first_name=str(data.get('first_name',''))[:150]
        if 'last_name' in data: person.last_name=str(data.get('last_name',''))[:150]
        user_fields=[field for field in ('username','first_name','last_name') if field in data]
        if user_fields: person.save(update_fields=user_fields)
        profile.profile_bio=str(data.get('bio',profile.profile_bio or ''))[:500]
        for field, limit in [('home_address',300),('relationship_status',80),('education_status',300)]:
            if field in data: setattr(profile, field, str(data[field])[:limit])
        if data.get('last_seen_privacy') in {'everyone','followers','nobody'}: profile.last_seen_privacy=data['last_seen_privacy']
        if data.get('status_privacy') in {'everyone','followers','nobody'}: profile.status_privacy=data['status_privacy']
        if 'read_receipts' in data: profile.read_receipts=str(data['read_receipts']).lower() in ('1','true','yes')
        avatar = request.FILES.get('avatar')
        if avatar:
            try:
                from PIL import Image
                Image.open(avatar).verify()
                avatar.seek(0)
            except Exception:
                return JsonResponse({'error':'Please select a valid image file.'}, status=400)
            profile.profile_image=avatar
        profile.save()
    return JsonResponse({'profile':{**user_data(person,request),'followers':profile.followed_by.count(),'following':profile.follows.count(),'is_following':viewer_profile.follows.filter(pk=profile.pk).exists(),'posts':[post_data(p,request,request.user) for p in Meep.objects.filter(user=person).order_by('-created_at')[:50]]}})

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_follow(request, username):
    person=User.objects.filter(username=username,is_active=True).first()
    if not person:return JsonResponse({'error':'User not found.'},status=404)
    if person.pk==request.user.pk:return JsonResponse({'error':'You cannot follow yourself.'},status=400)
    profile,_=Profile.objects.get_or_create(user=request.user); target,_=Profile.objects.get_or_create(user=person)
    if profile.follows.filter(pk=target.pk).exists():profile.follows.remove(target); following=False
    else:profile.follows.add(target); following=True; notify(person,request.user,'follow',f'{request.user.username} started following you')
    return JsonResponse({'following':following,'followers':target.followed_by.count()})


@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_share(request, post_id):
    original = Meep.objects.filter(pk=post_id).first()
    if not original: return JsonResponse({'error': 'Post not found.'}, status=404)
    data = payload(request) or {}
    note = str(data.get('body', '')).strip()
    body = (note + ('\n\n' if note else '') + f'Reshared from @{original.user.username}:\n{strip_tags(original.body or "")}')[:50000]
    shared = Meep.objects.create(user=request.user, body=body, title=f'Shared: {original.title or "Post"}'[:255], category=original.category or 'General')
    return JsonResponse({'post': post_data(shared, request, request.user)}, status=201)

@csrf_exempt
@api_login_required
@require_http_methods(['POST'])
def mobile_change_password(request):
    data=payload(request) or {}
    old=str(data.get('old_password',''))
    new=str(data.get('new_password',''))
    if not request.user.check_password(old):
        return JsonResponse({'error':'Current password is incorrect.'},status=400)
    from django.contrib.auth.password_validation import validate_password
    from django.core.exceptions import ValidationError
    try: validate_password(new,request.user)
    except ValidationError as e: return JsonResponse({'error':' '.join(e.messages)},status=400)
    request.user.set_password(new)
    request.user.save(update_fields=['password'])
    return JsonResponse({'ok':True})

@csrf_exempt
@api_login_required
@require_http_methods(['GET','POST'])
def mobile_complaints(request):
    if request.method == 'GET':
        complaints=Complaint.objects.filter(user=request.user).order_by('-date','-id')[:100]
        return JsonResponse({'complaints':[{'id':c.id,'description':c.desc,'status':c.status,'date':c.date.isoformat(),'attachment':media_url(request,c.attachment)} for c in complaints]})
    data=payload(request) or {}
    description=str(data.get('description','')).strip()
    if len(description)<10 or len(description)>5000:
        return JsonResponse({'error':'Complaint must contain 10–5000 characters.'},status=400)
    file=request.FILES.get('attachment')
    if file and file.size > 10*1024*1024:
        return JsonResponse({'error':'Attachment must be under 10 MB.'},status=413)
    from django.utils import timezone
    complaint=Complaint.objects.create(user=request.user,name=request.user.get_full_name() or request.user.username,email=request.user.email,phone='',desc=description,date=timezone.localdate(),attachment=file)
    return JsonResponse({'id':complaint.pk,'status':complaint.status},status=201)

@api_login_required
@require_http_methods(['GET'])
def mobile_news_shorts(request):
    videos = Video.objects.select_related('user').order_by('-created_at')[:100]
    return JsonResponse({'shorts': [
        {'id': video.id, 'username': video.user.username, 'caption': video.caption,
         'video': media_url(request, video.video, resource_type='video'), 'created_at': video.created_at.isoformat()}
        for video in videos
    ]})

# Authenticated video editing endpoints (requires ffmpeg and ffprobe installed).
import os
import subprocess
import tempfile
from django.http import FileResponse
from django.views.decorators.http import require_POST

_VIDEO_TYPES = {'.mp4', '.mov', '.m4v', '.webm', '.mkv'}

def _read_video(request):
    upload = request.FILES.get('video')
    if not upload or upload.size > MAX_UPLOAD:
        raise ValueError('Select a video smaller than 25 MB.')
    extension = os.path.splitext(upload.name)[1].lower()
    if extension not in _VIDEO_TYPES:
        raise ValueError('Unsupported video format.')
    return upload, extension

def _run_media_command(args, timeout=120):
    try:
        return subprocess.run(args, capture_output=True, text=True, timeout=timeout, check=True).stdout
    except FileNotFoundError:
        raise ValueError('FFmpeg/FFprobe is not installed on the Django server.')
    except subprocess.TimeoutExpired:
        raise ValueError('Video processing timed out.')
    except subprocess.CalledProcessError:
        raise ValueError('Unable to process this video file.')

def _save_temp_video(upload, extension, directory):
    filename = os.path.join(directory, 'input' + extension)
    with open(filename, 'wb') as output:
        for chunk in upload.chunks(): output.write(chunk)
    return filename

def _probe_duration(filename):
    value = _run_media_command(['ffprobe', '-v', 'error', '-show_entries',
        'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', filename], 30).strip()
    duration = float(value)
    if not (0 < duration <= 3600): raise ValueError('Video duration must be between 0 and 60 minutes.')
    return duration

@csrf_exempt
@api_login_required
@require_POST
def mobile_video_info(request):
    try:
        upload, extension = _read_video(request)
        with tempfile.TemporaryDirectory() as directory:
            source = _save_temp_video(upload, extension, directory)
            return JsonResponse({'duration': _probe_duration(source)})
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)

@csrf_exempt
@api_login_required
@require_POST
def mobile_video_trim(request):
    try:
        upload, extension = _read_video(request)
        start = float(request.POST.get('start', '0'))
        end = float(request.POST.get('end', '0'))
        with tempfile.TemporaryDirectory() as directory:
            source = _save_temp_video(upload, extension, directory)
            duration = _probe_duration(source)
            if not (0 <= start < end <= duration + 0.1) or end - start < 0.5:
                raise ValueError('Invalid trim range (minimum 0.5 seconds).')
            destination = os.path.join(directory, 'trimmed.mp4')
            _run_media_command(['ffmpeg', '-nostdin', '-y', '-i', source,
                '-ss', str(start), '-t', str(end - start),
                '-map', '0:v:0', '-map', '0:a?', '-c:v', 'libx264', '-preset', 'veryfast',
                '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-movflags', '+faststart',
                '-fs', str(MAX_UPLOAD), destination], 180)
            if not os.path.exists(destination) or os.path.getsize(destination) > MAX_UPLOAD:
                raise ValueError('Edited video is too large. Select a shorter segment.')
            with open(destination, 'rb') as result: data = result.read()
        from django.http import HttpResponse
        response = HttpResponse(data, content_type='video/mp4')
        response['Content-Disposition'] = 'attachment; filename="trimmed.mp4"'
        return response
    except ValueError as exc:
        return JsonResponse({'error': str(exc)}, status=400)
