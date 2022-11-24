from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .forms import SignUpForm, LoginForm, ImageFileUploadForm, FileUploadForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse, HttpResponse
from .models import Profile, Message, UserActivity
from django.core.files.storage import FileSystemStorage
import os
import mimetypes
from agora_token_builder import RtcTokenBuilder
import random
import time
import json
from .agora_key.RtcTokenBuilder import RtcTokenBuilder, Role_Attendee
from pusher import Pusher
from django.contrib.auth import get_user_model
from datetime import datetime

# Create your views here.
# Instantiate a Pusher Client
pusher_client = Pusher(app_id=os.environ.get('PUSHER_APP_ID'),
                       key=os.environ.get('PUSHER_KEY'),
                       secret=os.environ.get('PUSHER_SECRET'),
                       ssl=True,
                       cluster=os.environ.get('PUSHER_CLUSTER')
                       )

# Register
def register_user(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            return redirect("/")
        else:
            messages.error(request, 'Form is not valid.')
    else:
        form = SignUpForm()

    return render(request, "auth/register.html", {"form": form, "msg": msg, "success": success})

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST or None)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("chat/")
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    form = LoginForm()
    return render(request=request, template_name="auth/login.html", context={"form":form})

def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'

@login_required
def chat(request):
    all_users = User.objects.exclude(id=request.user.id).only('id', 'username')
    file_form = FileUploadForm(request.FILES)
    form = ImageFileUploadForm(request.POST, request.FILES,instance=request.user.profile)
    if is_ajax(request=request) and request.method == 'POST':
        if form.is_valid():
            form.save()
            return JsonResponse({'success': True, 'message': 'Image Uploaded Successfully!','bio': request.POST['bio']})
        else:
            return JsonResponse({'error': True, 'errors': form.errors})
    else:
        form = ImageFileUploadForm(instance=request.user.profile)
    return render(request, "chat.html",{'form': form,'file_form':file_form,'all_users':all_users})

def chatSendImage(request):
    user = User.objects.filter(username=request.POST.get('currentRecipient')).first()
    form = FileUploadForm(request.POST,request.FILES)
    if is_ajax(request=request) and request.method == 'POST':
        if form.is_valid():
            fileform = form.save(commit=False)
            fileform.user = request.user
            fileform.recipient_id = user.id
            fileform.save()
            return JsonResponse({'success': True, 'message': 'Image Uploaded Successfully!'})
    return JsonResponse({'success': True, 'message': 'Image Uploaded Successfully!'})

def download_file(request,path):
    file_path = os.path.join(settings.MEDIA_ROOT,path)
    if os.path.exists(file_path):
        with open(file_path,'rb') as fh:
            response = HttpResponse(fh.read(),content_type='application/chat_img')
            response['Content-Disposition'] = 'inline;filename=' + os.path.basename(file_path)
            return response

    raise Http404

def pusher_auth(request):
    payload = pusher_client.authenticate(
        channel=request.POST['channel_name'],
        socket_id=request.POST['socket_id'],
        custom_data={
            'user_id': request.user.id,
            'user_info': {
                'id': request.user.id,
                'name': request.user.username
            }
        })
    return JsonResponse(payload)


def generate_agora_token(request):
    appID = os.environ.get('AGORA_APP_ID')
    appCertificate = os.environ.get('AGORA_APP_CERTIFICATE')
    channelName = json.loads(request.body.decode(
        'utf-8'))['channelName']
    userAccount = request.user.username
    expireTimeInSeconds = 3600
    currentTimestamp = int(time.time())
    privilegeExpiredTs = currentTimestamp + expireTimeInSeconds

    token = RtcTokenBuilder.buildTokenWithAccount(
        appID, appCertificate, channelName, userAccount, Role_Attendee, privilegeExpiredTs)

    return JsonResponse({'token': token, 'appID': appID})

def call_user(request):
    body = json.loads(request.body.decode('utf-8'))
    user_to_call = body['user_to_call']
    channel_name = body['channel_name']
    caller = request.user.id

    pusher_client.trigger(
        'presence-online-channel',
        'make-agora-call',
        {
            'userToCall': user_to_call,
            'channelName': channel_name,
            'from': caller
        }
    )
    return JsonResponse({'message': 'call has been placed'})

def urlOnline(request):
    return JsonResponse({'message': 'success'})
