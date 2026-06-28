from django.urls import path
from .views import *
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('home/', index, name='home'),
    path('', loginn, name='login'),
    path('register/', register, name='register'),
    path('verify/', verify_otp, name='verify_otp'),
    path('consumers/', echo, name='consumers'),
    path('logout/', logoutt, name='logout'),
    path('1-on-1_chat/<int:room_id>/', one_on_one, name='one_on_one'),
    path('group_chat/<int:room_id>/', group_chat, name='group_chat'),
    path('media_sent/', addandfetchmedia, name='media_sent'),
    path('call/', call, name='call'),
    path('leave_call/', leave_call, name='leave_call'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
