import json

from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async

from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_title = self.scope['url_route']['kwargs']['pk']
        self.room_group_name = 'chat_%s' % self.post_title

        # Join room
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
    
    async def disconnect(self, close_code):
        # Leave room
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        firstName = data['firstName']
        postPk = data['postPk']

        await self.save_message(firstName, postPk, message)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'firstName': firstName
            }
        )
    
    async def chat_message(self, event):
        message = event['message']
        firstName = event['firstName']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'firstName': firstName
        }))

    @sync_to_async
    def save_message(self, firstName, postPk, message):
        Message.objects.create(firstName=firstName, postPk=postPk, content=message)