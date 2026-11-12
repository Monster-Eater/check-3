import uuid
from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import User
from django.db import IntegrityError, transaction
from django.utils import timezone
from .models import Group, GroupMessage, GroupMessageReceipt, Message
from home.models import Meep, PostReceipt


class CampusConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.user = self.scope.get('user')
        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return
        self.user_group = f'user_{self.user.pk}'
        await self.channel_layer.group_add(self.user_group, self.channel_name)
        await self.channel_layer.group_add('campus_feed', self.channel_name)
        await self.accept('campus.v1' if 'campus.v1' in self.scope.get('subprotocols', []) else None)
        pending = await self.mark_delivered_on_connect()
        for sender_id, ids in pending.items():
            await self.channel_layer.group_send(f'user_{sender_id}', {'type': 'receipt.event', 'payload': {'type':'message.delivered','message_ids':ids}})
        await self.send_json({'type': 'ready'})

    async def disconnect(self, code):
        if getattr(self, 'user_group', None):
            await self.channel_layer.group_discard(self.user_group, self.channel_name)
        for group_name in getattr(self, 'joined_groups', set()):
            await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        action = str(content.get('type', ''))
        if action == 'group.subscribe':
            group_id = content.get('group_id')
            if await self.can_join_group(group_id):
                name = f'chat_group_{int(group_id)}'
                await self.channel_layer.group_add(name, self.channel_name)
                if not hasattr(self, 'joined_groups'):
                    self.joined_groups = set()
                self.joined_groups.add(name)
                await self.send_json({'type': 'group.subscribed', 'group_id': int(group_id)})
        elif action == 'direct.send':
            await self.send_direct(content)
        elif action == 'group.send':
            await self.send_group(content)
        elif action == 'feed.send':
            await self.send_feed_post(content)
        elif action == 'message.seen':
            result = await self.mark_direct_seen(content.get('username'))
            if result:
                await self.channel_layer.group_send(f'user_{result[0]}', {'type': 'receipt.event', 'payload': result[1]})
                await self.send_json({'type': 'receipt.ack', 'kind': 'direct', 'count': result[2]})
        elif action == 'message.delivered':
            sender_id = await self.mark_direct_delivered(content.get('message_id'))
            if sender_id:
                await self.channel_layer.group_send(f'user_{sender_id}', {'type':'receipt.event','payload':{'type':'message.delivered','message_id':int(content['message_id'])}})
        elif action == 'group.delivered':
            result = await self.mark_group_delivered(content.get('group_id'), content.get('message_id'))
            if result:
                await self.channel_layer.group_send(f'chat_group_{result[0]}', {'type':'receipt.event','payload':{'type':'group.receipt','group_id':result[0],'user_id':self.user.pk,'delivered':True}})
        elif action == 'group.seen':
            result = await self.mark_group_seen(content.get('group_id'))
            if result:
                await self.channel_layer.group_send(f'chat_group_{result[0]}', {'type': 'receipt.event', 'payload': result[1]})
                await self.send_json({'type': 'receipt.ack', 'kind': 'group', 'group_id': result[0]})
        elif action == 'post.seen':
            result = await self.mark_post_seen(content.get('post_id'))
            if result:
                event = {'type': 'post.receipt', 'post_id': result, 'user_id': self.user.pk, 'seen': True}
                await self.channel_layer.group_send('campus_feed', {'type': 'receipt.event', 'payload': event})
                await self.send_json({'type': 'receipt.ack', 'kind': 'post', 'post_id': result})

    async def send_direct(self, data):
        result = await self.create_direct(data)
        if not result:
            await self.send_json({'type': 'error', 'message': 'Recipient or message is invalid.'})
            return
        recipient_id, payload = result
        await self.channel_layer.group_send(f'user_{recipient_id}', {'type': 'chat.event', 'payload': payload})
        await self.send_json({'type': 'chat.ack', **payload})

    async def send_group(self, data):
        result = await self.create_group(data)
        if not result:
            await self.send_json({'type': 'error', 'message': 'Group access denied or message is invalid.'})
            return
        group_id, payload = result
        await self.channel_layer.group_send(f'chat_group_{group_id}', {'type': 'chat.event', 'payload': payload})
        await self.send_json({'type': 'chat.ack', **payload})

    async def send_feed_post(self, data):
        result = await self.create_feed_post(data)
        if not result:
            await self.send_json({'type':'error','message':'Post text is empty or invalid.'})
            return
        payload, created = result
        if created:
            await self.channel_layer.group_send('campus_feed', {'type':'post.event','payload':payload})
        await self.send_json({'type':'feed.ack', **payload})

    async def chat_event(self, event):
        await self.send_json({'type': 'chat.message', **event['payload']})

    async def post_event(self, event):
        await self.send_json({'type': 'feed.post', **event['payload']})

    async def receipt_event(self, event):
        await self.send_json(event['payload'])

    @database_sync_to_async
    def can_join_group(self, group_id):
        return bool(group_id and Group.objects.filter(pk=group_id, members=self.user).exists())

    @database_sync_to_async
    def create_direct(self, data):
        username = str(data.get('username', ''))
        text = str(data.get('message', '')).strip()
        try:
            client_id = uuid.UUID(str(data.get('client_id')))
        except (ValueError, TypeError, AttributeError):
            return None
        recipient = User.objects.filter(username=username, is_active=True).first()
        if not recipient or recipient.pk == self.user.pk or not text or len(text) > 10000:
            return None
        reply_to = Message.objects.filter(pk=data.get('reply_to_id'), sender__in=[self.user, recipient], receiver__in=[self.user, recipient]).first() if data.get('reply_to_id') else None
        msg, created = Message.objects.get_or_create(sender=self.user, client_id=client_id, defaults={'receiver': recipient, 'message': text, 'reply_to': reply_to})
        if msg.receiver_id != recipient.pk:
            return None
        payload = {'kind': 'direct', 'id': msg.pk, 'client_id': str(client_id), 'sender': self.user.username, 'sender_id': self.user.pk, 'recipient': recipient.username, 'message': msg.message, 'timestamp': msg.timestamp.isoformat(), 'is_read': bool(msg.read_at), 'is_delivered': bool(msg.delivered_at)}
        return recipient.pk, payload

    @database_sync_to_async
    def create_group(self, data):
        try:
            group_id = int(data.get('group_id'))
            client_id = uuid.UUID(str(data.get('client_id')))
        except (ValueError, TypeError, AttributeError):
            return None
        text = str(data.get('message', '')).strip()
        if not text or len(text) > 10000:
            return None
        group = Group.objects.filter(pk=group_id, members=self.user).first()
        if not group:
            return None
        reply_to = GroupMessage.objects.filter(pk=data.get('reply_to_id'), group=group).first() if data.get('reply_to_id') else None
        msg, created = GroupMessage.objects.get_or_create(group=group, sender=self.user, client_id=client_id, defaults={'message': text, 'reply_to': reply_to})
        if created:
            for member in group.members.exclude(pk=self.user.pk):
                GroupMessageReceipt.objects.get_or_create(message=msg, user=member)
        payload = {'kind': 'group', 'group_id': group.pk, 'id': msg.pk, 'client_id': str(client_id), 'sender': self.user.username, 'sender_id': self.user.pk, 'message': msg.message or '', 'timestamp': msg.timestamp.isoformat()}
        return group.pk, payload

    @database_sync_to_async
    def create_feed_post(self, data):
        try:
            client_id = uuid.UUID(str(data.get('client_id')))
        except (ValueError, TypeError, AttributeError):
            return None
        body = str(data.get('body','')).strip()
        if not body or len(body) > 50000:
            return None
        post, created = Meep.objects.get_or_create(user=self.user, client_id=client_id, defaults={'body':body,'title':str(data.get('title','Campus update'))[:255],'category':str(data.get('category','General'))[:255]})
        payload = {'id':post.pk,'client_id':str(client_id),'username':self.user.username,'user_id':self.user.pk,'title':post.title,'body':body,'category':post.category,'created_at':post.created_at.isoformat(),'likes':0,'liked':False,'attachment':'','attachment_name':'','comments_count':0,'is_mine':True}
        return payload, created

    @database_sync_to_async
    def mark_direct_seen(self, username):
        other = User.objects.filter(username=username).first()
        if not other:
            return None
        now = timezone.now()
        count = Message.objects.filter(sender=other, receiver=self.user, read_at__isnull=True).update(read_at=now)
        return (other.pk, {'type': 'message.receipt', 'username': self.user.username, 'seen': True}, count) if count else None

    @database_sync_to_async
    def mark_direct_delivered(self, message_id):
        msg = Message.objects.filter(pk=message_id, receiver=self.user, delivered_at__isnull=True).first()
        if not msg:
            return None
        msg.delivered_at = timezone.now()
        msg.save(update_fields=['delivered_at'])
        return msg.sender_id

    @database_sync_to_async
    def mark_group_delivered(self, group_id, message_id):
        group = Group.objects.filter(pk=group_id, members=self.user).first()
        msg = GroupMessage.objects.filter(pk=message_id, group=group).first() if group else None
        if not msg or msg.sender_id == self.user.pk:
            return None
        receipt, _ = GroupMessageReceipt.objects.get_or_create(message=msg, user=self.user)
        if receipt.delivered_at:
            return None
        receipt.delivered_at = timezone.now()
        receipt.save(update_fields=['delivered_at'])
        return group.pk

    @database_sync_to_async
    def mark_delivered_on_connect(self):
        pending = {}
        now = timezone.now()
        for msg in Message.objects.filter(receiver=self.user, delivered_at__isnull=True).only('id','sender_id'):
            pending.setdefault(msg.sender_id, []).append(msg.pk)
        Message.objects.filter(receiver=self.user, delivered_at__isnull=True).update(delivered_at=now)
        return pending

    @database_sync_to_async
    def mark_group_seen(self, group_id):
        group = Group.objects.filter(pk=group_id, members=self.user).first()
        if not group:
            return None
        now = timezone.now()
        changed = False
        with transaction.atomic():
            recent_ids = list(group.messages.order_by('-timestamp').values_list('id', flat=True)[:300])
            for msg in group.messages.filter(id__in=recent_ids).exclude(sender=self.user):
                receipt, _ = GroupMessageReceipt.objects.get_or_create(message=msg, user=self.user)
                if not receipt.seen_at:
                    receipt.seen_at = now
                    receipt.delivered_at = receipt.delivered_at or now
                    receipt.save(update_fields=['seen_at', 'delivered_at'])
                    changed = True
        return (group.pk, {'type': 'group.receipt', 'group_id': group.pk, 'user_id': self.user.pk, 'seen': True}) if changed else None

    @database_sync_to_async
    def mark_post_seen(self, post_id):
        post = Meep.objects.filter(pk=post_id).first()
        if not post or post.user_id == self.user.pk:
            return None
        now = timezone.now()
        receipt, _ = PostReceipt.objects.get_or_create(post=post, user=self.user)
        changed = not bool(receipt.seen_at)
        if not receipt.seen_at:
            receipt.seen_at = now
            receipt.delivered_at = receipt.delivered_at or now
            receipt.save(update_fields=['seen_at', 'delivered_at'])
        return post.pk if changed else None
