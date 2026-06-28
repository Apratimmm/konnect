import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from channels_presence.models import Room

# class Echo_Consumer(AsyncWebsocketConsumer):
#
#     async def connect(self):
#         await self.accept()
#         await self.send(text_data=json.dumps({"type":"server_text","message": "actually connected with consumer"}))
#
#     async def disconnect(self, close_code):
#         pass
#
#     async def receive(self, text_data=None, bytes_data=None):
#         texttt = json.loads(text_data)
#         textttt = texttt.get('sent_text','')
#         if not textttt:
#             await self.send(text_data=json.dumps({"type":"empty_text","message": "you sent nothing"}))
#         else:
#             await self.send(text_data=json.dumps({"type":"echoed_text","message": textttt}))

async def chat_message(self, text_data):
    texttt = json.loads(text_data)
    textttt = texttt.get('sent_text', '')
    username = texttt.get('user', '')
    new_chat_name = texttt.get('rename_chat')
    media_url = texttt.get('media_url')
    media_type = texttt.get('media_type')
    call_initiate = texttt.get('call_initiate')

    if new_chat_name:
        await self.channel_layer.group_send(self.group_name, {"type": "rename", "new_chat_name": new_chat_name})
        return

    if media_url:
        await self.channel_layer.group_send(self.group_name, {
            "type": "media",
            "media_url": media_url,
            "media_type": media_type,
            "user": username
        })

    elif textttt:
        await self.channel_layer.group_send(self.group_name, {
            "type": "chat",
            "message": textttt,
            "user": username
        })

    elif call_initiate:
        await self.channel_layer.group_send(self.group_name, {
            "type": "call",
            "user": username
        })

    elif texttt.get('call_join'):
        await self.channel_layer.group_send(self.group_name, {
            "type": "call_join",
            "user": username
        })

    elif texttt.get('call_leave'):
        await self.channel_layer.group_send(self.group_name, {
            "type": "call_leave",
            "user": username
        })

class BaseChatConsumer(AsyncWebsocketConsumer):

    async def media(self, event):
        await self.send(text_data=json.dumps({ "type": "media_file",
            "media_url": event.get("media_url"),
            "media_type": event.get("media_type"),
            "user": event.get("user")
        }))

    async def chat(self, event):
        await self.send(text_data=json.dumps({"type": "chat_message", "message": event["message"], "user": event["user"]}))

    async def call(self, event):
        await self.send(text_data=json.dumps({"type": "call_initiate", "user": event["user"]}))

    async def call_join(self, event):
        await self.send(text_data=json.dumps({"type": "call_join_event", "user": event["user"]}))

    async def call_leave(self, event):
        await self.send(text_data=json.dumps({"type": "call_leave_event", "user": event["user"]}))

    async def rename(self, event):
        await self.send(text_data=json.dumps({"type": "chat_rename", "new_chat_name": event["new_chat_name"]}))

    async def connected(self, event):
        await self.send(text_data=json.dumps({"type": "user_connected", "message": event["message"]}))

    async def disconnected(self, event):
        await self.send(text_data=json.dumps({"type": "user_disconnected", "message": event["message"]}))

class One_on_OneConsumer(BaseChatConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.curr_username = self.scope['url_route']['kwargs']['username']
        self.group_name = f'group_{self.room_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await database_sync_to_async(Room.objects.add)(self.group_name, self.channel_name)

        room = await database_sync_to_async(Room.objects.get)(channel_name=self.group_name)
        user_count = await database_sync_to_async(lambda: room.presence_set.count())()

        if user_count > 2:
            await database_sync_to_async(Room.objects.remove)(self.group_name, self.channel_name)
            await self.channel_layer.group_send(self.group_name, {"type": "tried_connecting", "message": f"Tried Connecting: {self.curr_username}"})
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            await self.accept()
            await self.send(text_data=json.dumps({"type": "max_members", "message": "Already two people in the chat room"}))
            await self.close(123)
            return

        await self.accept()
        await self.send(text_data=json.dumps({"type": "channel_info", "message": self.channel_name}))
        await self.channel_layer.group_send(self.group_name, {"type": "connected", "message": f"Connected: {self.curr_username}"})

    async def receive(self, text_data=None, bytes_data=None):
        await chat_message(self, text_data)

    async def tried_connecting(self, event):
        await self.send(text_data=json.dumps({"type": "tried_connecting", "message": event["message"]}))

    async def disconnect(self, close_code):
        await database_sync_to_async(Room.objects.remove)(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        if close_code != 123:
            await self.channel_layer.group_send(self.group_name, {"type": "disconnected", "message": f"Disconnected: {self.curr_username}"})

class GroupConsumer(BaseChatConsumer):

    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.curr_username = self.scope['url_route']['kwargs']['username']
        self.group_name = f'group_{self.room_id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await database_sync_to_async(Room.objects.add)(self.group_name, self.channel_name)
        await self.accept()
        await self.send(text_data=json.dumps({"type": "channel_info", "message": self.channel_name}))
        await self.channel_layer.group_send(self.group_name, {"type": "connected", "message": f"Connected: {self.curr_username}"})

    async def receive(self, text_data=None, bytes_data=None):
        await chat_message(self, text_data)

    async def disconnect(self, code):
        await database_sync_to_async(Room.objects.remove)(self.group_name, self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_send(self.group_name, {"type": "disconnected", "message": f"Disconnected: {self.curr_username}"})