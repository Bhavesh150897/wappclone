from django.db.models import Q, Count, OuterRef, Subquery
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.authentication import SessionAuthentication

from wappclone import settings
from chat.serializers import MessageSerializer, UserSerializer
from chat.models import Message


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    SessionAuthentication scheme used by DRF. DRF's SessionAuthentication uses
    Django's session framework for authentication which requires CSRF to be
    checked. In this case we are going to disable CSRF tokens for the API.
    """

    def enforce_csrf(self, request):
        return

# class MessagePagination(PageNumberPagination):
#     """
#     Limit message prefetch to one page.
#     """
#     page_size = settings.MESSAGES_TO_LOAD


class MessageViewSet(ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    allowed_methods = ('GET', 'POST', 'HEAD', 'OPTIONS')
    authentication_classes = (CsrfExemptSessionAuthentication,)
    # pagination_class = MessagePagination

    def list(self, request, *args, **kwargs):
        self.queryset = self.queryset.filter(Q(recipient=request.user) |
                                             Q(user=request.user))
        target = self.request.query_params.get('target', None)
        if target is not None:
            self.queryset = self.queryset.filter(
                Q(recipient=request.user, user__username=target) |
                Q(recipient__username=target, user=request.user))
        return super().list(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        msg = get_object_or_404(
            self.queryset.filter(Q(recipient=request.user) |
                                 Q(user=request.user),
                                 Q(pk=kwargs['pk'])))
        serializer = self.get_serializer(msg)
        return Response(serializer.data)

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    allowed_methods = ('GET', 'HEAD', 'OPTIONS')
    pagination_class = None  # Get all user

    def list(self, request, *args, **kwargs):
        user = request.user
        # Get all users except yourself
        self.queryset = self.queryset.exclude(id=user.id)
        
        # get latest message along with users
        newest = Message.objects.filter(Q(recipient=user)|Q(user=user)).filter(
            Q(recipient_id=OuterRef('pk'))|Q(user_id=OuterRef('pk'))
        )       
        
        self.queryset = self.queryset.annotate(
            latest_message=Subquery(newest.values('body').order_by('-timestamp')[:1]),
            timestamp=Subquery(newest.values('timestamp').order_by('-timestamp')[:1]),
        )

        return super().list(request, *args, **kwargs)