from django.contrib import admin
from .models import Event
from .models import Venue
from .models import MyClubUser, Category, Comment
from .models import Profile, Meep, Complaint, Video, PostReport
from django.contrib.auth.models import User, Group

admin.site.unregister (Group)
admin.site.register(Profile)
admin.site.register(MyClubUser)
@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'date', 'status')
    list_filter = ('status', 'date')
    search_fields = ('name', 'email', 'desc', 'user__username')
    readonly_fields = ('user', 'date')
admin.site.register(Category)
admin.site.register(Video)
admin.site.register(Comment)

@admin.register(PostReport)
class PostReportAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'reporter', 'reason', 'status', 'created_at')
    list_filter = ('status', 'reason', 'created_at')
    search_fields = ('post__title', 'post__user__username', 'reporter__username', 'details')
    readonly_fields = ('post', 'reporter', 'reason', 'details', 'created_at')

class ProfileInline(admin.StackedInline):
    model = Profile


class UserAdmin(admin.ModelAdmin):
    model = User    
    fields = ['username']
    inlines = [ProfileInline]

admin.site.unregister (User)   
admin.site.register(User, UserAdmin)
admin.site.register(Meep)
   


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "phone")
    ordering = ("name",)
    search_fields = ("name", "address")

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    fields = (("name", "venue"), 'event_date', 'description', 'manager' )
    list_display = ('name', "event_date", "venue") 
    list_filter = ('event_date', 'venue')
    ordering = ('-event_date',)

