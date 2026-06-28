import random
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from . import settings
from .forms import UserCreateForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from main.models import Media, in_call, OTPVerification, User
from django.contrib.auth import login, logout, user_logged_in
from django.http import JsonResponse
from livekit import api
import os
from datetime import timedelta
from django.views.decorators.csrf import csrf_exempt
from channels_presence.models import Presence

api_key = os.environ['LIVEKIT_API_KEY']
api_secret_key = os.environ['LIVEKIT_API_SECRET']
url = os.environ['LIVEKIT_URL']


def echo(request):
    return render(request, 'consumers.html')

@login_required(login_url='login')
def index(request):
    return render(request, 'home.html')

def clear_table(request, template, room_id):
    response = render(request, template, {'room_id': room_id})
    channel = request.COOKIES.get('channel_name')
    if channel:
        Presence.objects.filter(channel_name=channel).delete()
    response.delete_cookie('channel_name', path='/')
    return response

@login_required(login_url='login', redirect_field_name='redirect_to')
def one_on_one(request, room_id):
    return clear_table(request, '1_on_1.html', room_id)

@login_required(login_url='login', redirect_field_name='redirect_to')
def group_chat(request, room_id):
    return clear_table(request, 'group_chat.html', room_id)

def addandfetchmedia(request):
    if request.method != 'POST':
        return JsonResponse({'status':'failed'})

    room_id = request.POST.get('room_id')
    username = request.POST.get('username')
    file = request.FILES['file']

    extension = file.name.lower().split('.')[-1]
    if extension in ['png', 'jpg', 'jpeg', 'gif']:
        media_type = 'image'
    elif extension in ['mp4', 'webm', 'mkv', 'avi', 'mov']:
        media_type = 'video'
    else:
        media_type = 'audio'

    recent = Media.objects.create(
        username=username,
        room=room_id,
        file=file,
        media_type=media_type
    )

    media_url = request.build_absolute_uri(recent.file.url)
    return JsonResponse({'status':'success',
                         'url': media_url,
                         'media_type': media_type})

def register(request):
    if request.method == 'GET':
        form = UserCreateForm()
        return render(request, 'register.html', {'form': form})
    else:
        form = UserCreateForm(data=request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()

            otp= str(random.randint(100000, 999999))
            OTPVerification.objects.create(user=user, otp=otp)

            send_mail(
                subject="Konnect Verification",
                message=f"""
                            Hi {user.username},

                            OTP : {otp}

                            Validity : 1 minute""",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

            request.session['user_id'] = user.id
            return redirect(to='verify_otp')
        else:
            return render(request, 'register.html', {'form': form})

def verify_otp(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect(to='login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect(to='login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp').strip() if request.POST.get('otp') else ''

        otp_present = OTPVerification.objects.filter(
            user=user,
            otp=entered_otp,
            is_used=False).first()

        if otp_present and not otp_present.is_expired():
            otp_present.delete()

            user.is_active = True
            user.save()

            login(request, user)
            return redirect('home')

        else:
            return render(request, 'verify_otp.html', {'error': 'Invalid or expired OTP'})

    return render(request, 'verify_otp.html')


def loginn(request):
    if request.method == 'GET':
        redirect_to = request.GET.get('redirect_to')
        form = UserLoginForm()
        return render(request, 'login.html', {'form': form, 'redirect_to': redirect_to})
    else:
        redirect_to = request.POST.get('redirect_to')
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if redirect_to:
                return redirect(redirect_to)
            return redirect(to='home')
        else:
            return render(request, 'login.html', {'form': form})

def logoutt(request):
    logout(request)
    return redirect(to='login')

def call(request):
    username = request.user.username
    room_id = request.GET.get('room')

    is_in_call = in_call.objects.filter(username=username).first()
    if is_in_call:
        if is_in_call.room != room_id:
            return JsonResponse({'room': is_in_call.room})
    else:
        in_call.objects.create(username=username, room=room_id)

    video_info = api.access_token.VideoGrants()
    video_info.room_join = True
    video_info.room = room_id
    video_info.can_publish = True
    video_info.can_subscribe = True
    video_info.can_publish_video = True 

    access_token = api.access_token.AccessToken(api_key, api_secret_key)
    access_token.with_ttl(timedelta(hours=6))
    access_token.with_grants(video_info)
    access_token.with_identity(username)
    access_token.with_name(username)
    
    token = access_token.to_jwt()
    
    return render(request, 'call.html', {
        'token': token, 
        'url': url, 
        'room_id': room_id,
        'username': username
    })

@csrf_exempt
def leave_call(request):
    username = request.user.username
    in_call.objects.filter(username=username).delete()
    return JsonResponse({'status': 'left'})