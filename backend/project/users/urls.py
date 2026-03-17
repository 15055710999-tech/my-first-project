from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.profile, name='profile'),  # 确保这一行存在
    path('info/', views.get_user_info, name='get_user_info'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('avatar/', views.upload_avatar, name='upload_avatar'),
]