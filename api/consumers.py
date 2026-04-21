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



# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import sync_to_async
# from django.contrib.auth import get_user_model
# from .models import Chat, Message
# from api.models import Appointment

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
#                     "sender": msg.sender.username or msg.sender.email,
#                     "sender_id": msg.sender_id,
#                     "receiver": msg.receiver.username or msg.receiver.email,
#                     "receiver_id": msg.receiver_id,
#                     "message_id": msg.id,
#                 }
#             )

#         # 🔹 SEEN
#         elif data.get("type") == "seen":
#             message_id = data.get("message_id")
#             if not message_id:
#                 return

#             await self.mark_seen(message_id)

#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 {
#                     "type": "seen_update",
#                     "message_id": message_id
#                 }
#             )

#         # 🔹 WEBRTC SIGNAL (FIXED)
#         elif data.get("type") in ["offer", "answer", "candidate"]:
#             await self.channel_layer.group_send(
#                 self.room_group_name,
#                 data   # ✅ send same data
#             )

#     # 🔹 CHAT MESSAGE
#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps(event))

#     # 🔹 SEEN UPDATE
#     async def seen_update(self, event):
#         await self.send(text_data=json.dumps(event))

#     # 🔹 WEBRTC EVENTS (IMPORTANT)
#     async def offer(self, event):
#         await self.send(text_data=json.dumps(event))

#     async def answer(self, event):
#         await self.send(text_data=json.dumps(event))

#     async def candidate(self, event):
#         await self.send(text_data=json.dumps(event))

#     # ================= DB =================

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




import asyncio
import json
from datetime import datetime

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Appointment, Chat, Message

User = get_user_model()
CALL_STATE_LOCK = asyncio.Lock()
APPOINTMENT_CALL_STATES = {}


def _appointment_slot_is_active(appointment):
    now = timezone.localtime()
    slot_start = timezone.make_aware(
        datetime.combine(appointment.slot.date, appointment.slot.start_time)
    )
    slot_end = timezone.make_aware(
        datetime.combine(appointment.slot.date, appointment.slot.end_time)
    )
    return appointment.status == "scheduled" and slot_start <= now < slot_end


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.appointment_id = self.scope['url_route']['kwargs']['appointment_id']
        self.room_group_name = f"chat_{self.appointment_id}"
        self.user = self.scope.get("user")

        if not self.user or not self.user.is_authenticated:
            await self.close(code=4401)
            return

        self.appointment = await self.get_appointment_for_user()
        if not self.appointment:
            await self.close(code=4403)
            return

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        call_was_active = await self.clear_call_state_for_current_channel()
        if call_was_active:
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": {
                        "type": "end_call",
                        "message": "Call ended because one participant disconnected."
                    },
                    "sender_channel": self.channel_name
                }
            )

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # ================= RECEIVE =================
    async def receive(self, text_data):
        data = json.loads(text_data)
        slot_active = await self.is_slot_active()

        if data.get("type") in ["message", "seen", "offer", "answer", "candidate", "end_call", "reject_call"] and not slot_active:
            await self.send(text_data=json.dumps({
                "type": "slot_expired",
                "message": "Slot time has ended. Chat, audio, and video are disabled now."
            }))
            return

        # ================= CHAT =================
        if data.get("type") == "message":
            msg = await self.save_message(data)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": msg.message,
                    "sender_id": msg.sender_id,
                    "sender": msg.sender.username,
                    "receiver_id": msg.receiver_id,
                    "message_id": msg.id,
                    "is_read": msg.is_read,
                }
            )

        elif data.get("type") == "seen":
            message_id = data.get("message_id")
            if not message_id:
                return

            updated = await self.mark_seen(message_id)
            if not updated:
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "seen_update",
                    "message_id": message_id,
                }
            )

        # ================= WEBRTC =================
        elif data.get("type") == "offer":
            offer_registered = await self.register_call_offer(data.get("call_type"))
            if not offer_registered:
                await self.send(text_data=json.dumps({
                    "type": "call_busy",
                    "message": "Call already pending or connected for this appointment."
                }))
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": data,
                    "sender_channel": self.channel_name
                }
            )

        elif data.get("type") == "answer":
            await self.mark_call_connected()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": data,
                    "sender_channel": self.channel_name
                }
            )

        elif data.get("type") == "reject_call":
            call_cleared = await self.clear_call_state()
            if not call_cleared:
                return

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": {
                        "type": "call_rejected",
                        "message": "Remote user rejected the call."
                    },
                    "sender_channel": self.channel_name
                }
            )

        elif data.get("type") == "end_call":
            await self.clear_call_state()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": data,
                    "sender_channel": self.channel_name
                }
            )

        elif data.get("type") == "candidate":
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "webrtc_signal",
                    "data": data,
                    "sender_channel": self.channel_name
                }
            )

    # ================= SEND =================
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    async def seen_update(self, event):
        await self.send(text_data=json.dumps(event))

    async def webrtc_signal(self, event):
        # prevent sending back to self
        if self.channel_name != event["sender_channel"]:
            await self.send(text_data=json.dumps(event["data"]))

    async def register_call_offer(self, call_type):
        async with CALL_STATE_LOCK:
            existing_state = APPOINTMENT_CALL_STATES.get(self.appointment_id)
            if existing_state:
                existing_status = existing_state.get("status")
                existing_call_type = existing_state.get("call_type")

                # Allow connected audio<->video switch requests, but still block
                # duplicate requests for the same call type or any parallel ringing state.
                if existing_status == "ringing":
                    return False

                if existing_status == "connected" and existing_call_type == call_type:
                    return False

            APPOINTMENT_CALL_STATES[self.appointment_id] = {
                "status": "ringing",
                "call_type": call_type,
                "participant_channels": {self.channel_name},
            }
            return True

    async def mark_call_connected(self):
        async with CALL_STATE_LOCK:
            state = APPOINTMENT_CALL_STATES.get(self.appointment_id)
            if not state:
                return False

            state["status"] = "connected"
            participant_channels = state.setdefault("participant_channels", set())
            participant_channels.add(self.channel_name)
            return True

    async def clear_call_state(self):
        async with CALL_STATE_LOCK:
            return APPOINTMENT_CALL_STATES.pop(self.appointment_id, None) is not None

    async def clear_call_state_for_current_channel(self):
        async with CALL_STATE_LOCK:
            state = APPOINTMENT_CALL_STATES.get(self.appointment_id)
            if not state:
                return False

            participant_channels = state.get("participant_channels", set())
            if self.channel_name not in participant_channels:
                return False

            APPOINTMENT_CALL_STATES.pop(self.appointment_id, None)
            return True

    # ================= DB =================
    @sync_to_async
    def save_message(self, data):
        appointment = Appointment.objects.get(id=self.appointment_id)
        sender = User.objects.get(id=self.user.id)

        if sender == appointment.patient:
            receiver = appointment.doctor
        elif sender == appointment.doctor:
            receiver = appointment.patient
        else:
            raise PermissionError("Not allowed")

        chat, _ = Chat.objects.get_or_create(appointment=appointment)

        return Message.objects.create(
            chat=chat,
            sender=sender,
            receiver=receiver,
            message=data.get("message"),
        )

    @sync_to_async
    def is_slot_active(self):
        try:
            appointment = Appointment.objects.select_related("slot").get(id=self.appointment_id)
        except Appointment.DoesNotExist:
            return False
        return _appointment_slot_is_active(appointment)

    @sync_to_async
    def get_appointment_for_user(self):
        try:
            appointment = Appointment.objects.select_related("slot", "patient", "doctor").get(id=self.appointment_id)
        except Appointment.DoesNotExist:
            return None

        if self.user.id not in [appointment.patient_id, appointment.doctor_id]:
            return None

        return appointment

    @sync_to_async
    def mark_seen(self, message_id):
        try:
            msg = Message.objects.select_related("chat__appointment").get(id=message_id)
        except Message.DoesNotExist:
            return False

        if msg.chat.appointment_id != int(self.appointment_id):
            return False

        if msg.receiver_id != self.user.id:
            return False

        if msg.is_read:
            return True

        msg.is_read = True
        msg.save(update_fields=["is_read"])
        return True
