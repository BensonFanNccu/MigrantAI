from flask import Flask, request
from flask_socketio import SocketIO, join_room, leave_room, emit

from ..models import Message, Chat, db
from ..translate.trans import translate_helper
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

        if s_lang != r_lang:

            recv_res = translate_helper(s_lang, r_lang, text)
            # send_res = translate_helper(s_lang, s_lang, text)

            if recv_res["status"] != "success":
                emit("error", {"message": "translation failed"})
                return

            text_for_receiver = recv_res["translation"]
            text_for_sender = text

            terms_recv = recv_res.get("specialized_terms", [])

        else:
            text_for_receiver, text_for_sender = text, text
            terms_recv = []

        send_time = datetime.now()
        msg = Message(
            text_sender=text_for_sender,
            text_reciever=text_for_receiver,
            time=send_time,
            sender_id=sender,
            receiver_id=receiver,
        )
        db.session.add(msg)
        db.session.commit()

        chat_link = Chat(message_id=msg.id, chatroom_id=chatroom_id)
        db.session.add(chat_link)
        db.session.commit()

        base = {
            "chatroom_id": data["chatroom_id"],
            "from": data["sender_id"],
            "to": data["receiver_id"],
            "timestamp": send_time.isoformat(),
        }

        emit(
            "receive_message",
            {**base, "message": text_for_receiver, "specialized_terms": terms_recv},
            room=data["receiver_id"],
        )

        # 2) echo back to sender
        emit(
            "receive_message",
            {**base, "message": text_for_sender, "specialized_terms": []},
            room=data["sender_id"],
        )

    @socketio.on("disconnect")
    def on_disconnect():
        user_id = request.args.get("user_id")
        print(f"[WS] {user_id} disconnected")
