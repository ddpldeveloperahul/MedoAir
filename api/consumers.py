# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from django.contrib.auth.models import User
# from asgiref.sync import sync_to_async

# from .models import Chat, Message
# from api.models import Appointment
# from django.contrib.auth import get_user_model
# User = get_user_model()


# class ChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
#         self.room_group_name = f"chat_{self.appointment_id}"

#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )

#     # 🔥 RECEIVE
#     async def receive(self, text_data):
#         data = json.loads(text_data)

#         # 🔹 TEXT MESSAGE
#         if data.get("type") == "message":
#             msg = await self.save_message(data)

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "chat_message",
#                     "message": msg.message,
#                     "sender": msg.sender.email,
#                     "receiver": msg.receiver.email,
#                     "message_id": msg.id
#                 }
#             )

#         # 🔹 SEEN
#         elif data.get("type") == "seen":
#             await self.mark_seen(data["message_id"])

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "seen_update",
#                     "message_id": data["message_id"]
#                 }
#             )

#         # 🔹 WEBRTC SIGNALING
#         elif data.get("type") in ["offer", "answer", "candidate"]:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "webrtc_signal",
#                     "data": data
#                 }
#             )
#             # 🔹 SEND MESSAGE
#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps(event))

#     # 🔹 SEEN UPDATE
#     async def seen_update(self, event):
#         await self.send(text_data=json.dumps(event))

#     # 🔹 WEBRTC SIGNAL
#     async def webrtc_signal(self, event):
#         await self.send(text_data=json.dumps(event["data"]))
        
#     async def offer(self, event):
#         await self.send(text_data=json.dumps(event))

#     async def answer(self, event):
#         await self.send(text_data=json.dumps(event))

#     async def candidate(self, event):
#         await self.send(text_data=json.dumps(event))

#     # ================= DB OPERATIONS =================

#     @sync_to_async
#     def save_message(self, data):
#         appointment = Appointment.objects.get(id=self.appointment_id)
#         sender = User.objects.get(id=data["sender_id"])

#         if sender == appointment.patient:
#             receiver = appointment.doctor
#         else:
#             receiver = appointment.patient

#         chat, _ = Chat.objects.get_or_create(appointment=appointment)

#         return Message.objects.create(
#             chat=chat,
#             sender=sender,
#             receiver=receiver,
#             message=data.get("message"),
#         )

#     @sync_to_async
#     def mark_seen(self, message_id):
#         msg = Message.objects.get(id=message_id)
#         msg.is_read = True
#         msg.save()



import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.contrib.auth import get_user_model
from .models import Chat, Message
from api.models import Appointment

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
        self.room_group_name = f"chat_{self.appointment_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # 🔥 RECEIVE
    async def receive(self, text_data):
        data = json.loads(text_data)

        # 🔹 TEXT MESSAGE
        if data.get("type") == "message":
            msg = await self.save_message(data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg.message,
                    "sender": msg.sender.username or msg.sender.email,
                    "sender_id": msg.sender_id,
                    "receiver": msg.receiver.username or msg.receiver.email,
                    "receiver_id": msg.receiver_id,
                    "message_id": msg.id,
                }
            )

        # 🔹 SEEN
        elif data.get("type") == "seen":
            message_id = data.get("message_id")
            if not message_id:
                return

            await self.mark_seen(message_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "seen_update",
                    "message_id": message_id
                }
            )

        # 🔹 WEBRTC SIGNAL (FIXED)
        elif data.get("type") in ["offer", "answer", "candidate"]:
            await self.channel_layer.group_send(
                self.room_group_name,
                data   # ✅ send same data
            )

    # 🔹 CHAT MESSAGE
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    # 🔹 SEEN UPDATE
    async def seen_update(self, event):
        await self.send(text_data=json.dumps(event))

    # 🔹 WEBRTC EVENTS (IMPORTANT)
    async def offer(self, event):
        await self.send(text_data=json.dumps(event))

    async def answer(self, event):
        await self.send(text_data=json.dumps(event))

    async def candidate(self, event):
        await self.send(text_data=json.dumps(event))

    # ================= DB =================

    @sync_to_async
    def save_message(self, data):
        appointment = Appointment.objects.get(id=self.appointment_id)
        sender = User.objects.get(id=data["sender_id"])

        if sender == appointment.patient:
            receiver = appointment.doctor
        else:
            receiver = appointment.patient

        chat, _ = Chat.objects.get_or_create(appointment=appointment)

        return Message.objects.create(
            chat=chat,
            sender=sender,
            receiver=receiver,
            message=data.get("message"),
        )

    @sync_to_async
    def mark_seen(self, message_id):
        msg = Message.objects.get(id=message_id)
        msg.is_read = True
        msg.save()
