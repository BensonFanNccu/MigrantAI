from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit

from ..models   import Message, Chat, db
from datetime import datetime


def mock_translate(text, lang):

    return f"[{lang} translation] {text}"


def register_chat_handlers(socketio):

    @socketio.on("connect")
    def on_connect():
        # auth is a dict { 'user_id': 'alice' }
        user_id = request.args.get("user_id")
        if not user_id:
            print("[WS] Rejecting connection—no user_id")
            return False  # still returns 401 if missing
        join_room(user_id)
        print(f"[WS] {user_id} connected")

    @socketio.on("send_message")
    def handle_send_message(data):
        """
        data = {
        "chatroom_id": "...",
        "sender_id": "...",
        "receiver_id": "...",
        "text": "...",
        "sender_lang": "...",
        "receiver_lang": "..."
        }
        """
        required = {
            "chatroom_id",
            "sender_id",
            "receiver_id",
            "text",
            "sender_lang",
            "receiver_lang",
        }
        if not required.issubset(data):
            emit("error", {"message": "invalid payload"})
            return

        chatroom_id = data["chatroom_id"]
        sender = data["sender_id"]
        receiver = data["receiver_id"]
        text = data["text"]
        s_lang = data["sender_lang"]
        r_lang = data["receiver_lang"]


        text_for_receiver = mock_translate(text, r_lang)
        text_for_sender = mock_translate(text, s_lang)

        
        sned_time = datetime.now()
        msg = Message(
        text_sender = text_for_sender,
        text_reciever = text_for_receiver,
        time=sned_time,
        sender_id=sender,
        receiver_id=receiver
        )
        db.session.add(msg)
        db.session.commit()

        chat_link = Chat(
        message_id=msg.id,
        chatroom_id=chatroom_id
        )
        db.session.add(chat_link)
        db.session.commit()

        payload = {
            "chatroom_id": chatroom_id,
            "from": sender,
            "to": receiver,
            "timestamp": sned_time.isoformat(),
        }

        # push to receiver
        payload["message"] = text_for_receiver
        emit("receive_message", payload, room=receiver)

        # echo back to sender
        payload["message"] = text_for_sender
        emit("receive_message", payload, room=sender)

        # 3) Emit real-time via SocketIO

    @socketio.on("disconnect")
    def on_disconnect():
        user_id = request.args.get("user_id")
        print(f"[WS] {user_id} disconnected")
