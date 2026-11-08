from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import mobile_api



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('memberss/', include('django.contrib.auth.urls')),
    path('memberss/', include('memberss.urls')),
    path('chat/', include('chat.urls')),
    path('api/mobile/media/video-info/', mobile_api.mobile_video_info),
    path('api/mobile/media/trim/', mobile_api.mobile_video_trim),
    path('api/mobile/signup/', mobile_api.mobile_signup, name='mobile_signup'),
    path('api/mobile/login/', mobile_api.mobile_login, name='mobile_login'),
    path('api/mobile/me/', mobile_api.mobile_me, name='mobile_me'),
    path('api/mobile/change-password/', mobile_api.mobile_change_password),
    path('api/mobile/complaints/', mobile_api.mobile_complaints),
    path('api/mobile/news-shorts/', mobile_api.mobile_news_shorts, name='mobile_news_shorts'),
    path('api/mobile/feed/', mobile_api.mobile_feed, name='mobile_feed'),
    path('api/mobile/feed/<int:post_id>/like/', mobile_api.mobile_like, name='mobile_like'),
    path('api/mobile/contacts/', mobile_api.mobile_contacts, name='mobile_contacts'),
    path('api/mobile/chat/<str:username>/', mobile_api.mobile_chat, name='mobile_chat'),
    path('api/mobile/chat/<str:username>/presence/', mobile_api.mobile_presence, name='mobile_presence'),
    path('api/mobile/feed/<int:post_id>/comments/', mobile_api.mobile_comments, name='mobile_comments'),
    path('api/mobile/feed/<int:post_id>/share/', mobile_api.mobile_share, name='mobile_share'),
    path('api/mobile/groups/', mobile_api.mobile_groups, name='mobile_groups'),
    path('api/mobile/groups/<int:group_id>/', mobile_api.mobile_group_chat, name='mobile_group_chat'),
    path('api/mobile/groups/<int:group_id>/members/', mobile_api.mobile_group_members, name='mobile_group_members'),
    path('api/mobile/notifications/', mobile_api.mobile_notifications, name='mobile_notifications'),
    path('api/mobile/status/<int:status_id>/', mobile_api.mobile_status_detail),
    path('api/mobile/status/', mobile_api.mobile_status, name='mobile_status'),
    path('api/mobile/search/', mobile_api.mobile_search, name='mobile_search'),
    path('api/mobile/profile/<str:username>/', mobile_api.mobile_profile, name='mobile_profile'),
    path('api/mobile/profile/<str:username>/follow/', mobile_api.mobile_follow, name='mobile_follow'),
  
]+ static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT )
