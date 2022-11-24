from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from .models import Profile,UserActivity
from datetime import datetime

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    print('user {} logged in through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
    users = User.objects.get(id=user.id)
    obj = UserActivity.objects.filter(user_id=users.id).first()
    if obj != None:
        obj.online = 1
        obj.last_online_time = datetime.now()
        obj.save()
    else:
        obj = UserActivity(user=users, online=1, last_online_time=datetime.now())
        obj.save()

# @receiver(user_login_failed)
# def log_user_login_failed(sender, credentials, request, **kwargs):
#     print('user {} logged in failed through page {}'.format(credentials.get('username'), request.META.get('HTTP_REFERER')))

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    users = User.objects.get(id=user.id)
    print('user {} logged out through page {}'.format(user.username, request.META.get('HTTP_REFERER')))
    obj = UserActivity.objects.filter(user_id=users.id).first()
    if obj != None:
        obj.online = 0
        obj.last_online_time = datetime.now()
        obj.save()
    else:
        obj = UserActivity(user=users, online=0, last_online_time=datetime.now())
        obj.save()
