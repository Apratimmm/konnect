from .consumers import *
from django.urls import path

chat_url_patterns= [
    path('1-on-1_chat/<int:room_id>/<str:username>/', One_on_OneConsumer.as_asgi(), name='1_on_1'),
    path('group_chat/<int:room_id>/<str:username>/', GroupConsumer.as_asgi(), name='group_chat'),
]