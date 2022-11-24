from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from chat.models import Message
from rest_framework.serializers import ModelSerializer, CharField, DateTimeField, ImageField
from .forms import FileUploadForm

class MessageSerializer(ModelSerializer):
    user = CharField(source='user.username',read_only=True)
    recipient = CharField(source='recipient.username')
    profile = ImageField(source='user.profile.avatar',read_only=True)

    def create(self, validated_data):
        user = self.context['request'].user
        recipient = get_object_or_404(User, username=validated_data['recipient']['username'])
        msg = Message(recipient=recipient,
                           body=validated_data['body'],
                           user=user)
        msg.save()
        return msg

    class Meta:
        model = Message
        fields = '__all__'

class UserSerializer(ModelSerializer):
    latest_message = CharField()
    timestamp = DateTimeField()
    profile = ImageField(source='profile.avatar')
    online = CharField(source='useractivity.online',read_only=True)

    class Meta:
        model = User
        fields = '__all__'
