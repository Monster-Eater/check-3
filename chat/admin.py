from django.contrib import admin
from .models import Message, Group, GroupMessage, ChatInvite

admin.site.register(Message)
admin.site.register(Group)
admin.site.register(GroupMessage)
admin.site.register(ChatInvite)
