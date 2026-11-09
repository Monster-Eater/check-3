from . import views
from django.urls import path

# from django.contrib.auth import views as auth_views

urlpatterns = [
 
  # path('edit_profile/', UserEditView.as_view(), name = 'edit_profile'),
  # path('password/', PasswordsChangeView.as_view(template_name = 'registration/change-password.htm')),
  path('login_user', views.login_user, name = 'login'),
  path('logout_user', views.logout_user, name = 'logout'),
  path('register', views.register_user, name = 'register'),
  path('update_user', views.update_user, name = 'update_user'),
  path('update_password', views.update_password, name = 'update_password'),
  
]

 