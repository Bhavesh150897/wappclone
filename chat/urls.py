from django.urls import path, include, re_path
from .views import login_view, register_user, chat, chatSendImage, download_file, pusher_auth, generate_agora_token, call_user, urlOnline
from django.contrib.auth.views import LogoutView
from rest_framework.routers import DefaultRouter
from chat.api import MessageViewSet, UserViewSet
from django.conf.urls.static import static
from wappclone import settings
from django.views.static import serve

routers = DefaultRouter()
routers.register(r'message', MessageViewSet, basename='message-api')
routers.register(r'users', UserViewSet, basename='users-api')

urlpatterns = [
    path('api/v1/', include(routers.urls)),
    path('', login_view, name="login"),
    path('register/', register_user, name="register"),
    path('chat/', chat, name="chat"),
    path('send-img/', chatSendImage, name="chatSendImage"),
    path('online/', urlOnline, name="urlOnline"),
    path('pusher/auth/', pusher_auth, name='agora-pusher-auth'),
    path('token/', generate_agora_token, name='agora-token'),
    path('call-user/', call_user, name='agora-call-user'),
    re_path(r'^download-file/(?P<path>.*)$', serve, {'document_root':settings.MEDIA_ROOT}),
    path("logout/", LogoutView.as_view(), name="logout"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
