from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta

class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages')
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages')
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='chat_attachments/', blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.sender.username} to {self.receiver.username}: {self.message[:20]}"

class Group(models.Model):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField(User, related_name='chat_groups')
    icon = models.FileField(upload_to='group_icons/', blank=True, null=True)
    rules = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class GroupMessage(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField(blank=True, null=True)
    attachment = models.FileField(upload_to='chat_files/', blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.sender.username} in {self.group.name}: {self.message[:20]}"
    ChatMessage = Message

class OfficeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)

class ChatInvite(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invites')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_invites')
    is_accepted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

class ChatPresence(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='chat_presence')
    last_seen = models.DateTimeField(auto_now=True)
    typing_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name='typing_presence')
    typing_until = models.DateTimeField(blank=True, null=True)

class StatusUpdate(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='status_updates')
    text = models.CharField(max_length=500, blank=True)
    media = models.FileField(upload_to='status_updates/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def expires_at(self):
        return self.created_at + timedelta(hours=24)

    


class MobileAPIToken(models.Model):
    """Hashed bearer token used by the Flutter client (independent of browser cookies)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='mobile_api_tokens')
    token_hash = models.CharField(max_length=64, unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Mobile API token for {self.user.username}"


class SocialNotification(models.Model):
    KIND_CHOICES = [(k, k) for k in ('like', 'comment', 'follow', 'message', 'group', 'system')]
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_notifications')
    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_social_notifications')
    kind = models.CharField(max_length=20, choices=KIND_CHOICES, default='system')
    text = models.CharField(max_length=255)
    target_url = models.CharField(max_length=500, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.recipient}: {self.text}'


class StatusView(models.Model):
    status = models.ForeignKey(StatusUpdate, on_delete=models.CASCADE, related_name='views')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['status', 'user'], name='unique_status_viewer')]
