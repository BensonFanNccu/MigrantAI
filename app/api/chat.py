from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Chatroom, Chat, Message


auth_ct = Blueprint("chat", __name__)


@auth_ct.route("/create_chatroom", methods=["POST"])
#@jwt_required()
def create_chatroom():
    post_data = request.get_json()
    
    username_1 = post_data.get("user_1")
    username_2 = post_data.get("user_2")
    
    user1 = User.query.filter_by(username=username_1).first()
    user2 = User.query.filter_by(username=username_2).first()
    
    if username_1 == username_2:
        return jsonify({"status": "failure", "message": "Cannot create room by yourself"}), 409
    
    if not user1 or not user2:
        return jsonify({"status": "failure", "message": "User does not exist"}), 409
    
    new_room = Chatroom(user_1=user1.id, user_2=user2.id)
    db.session.add(new_room)
    db.session.commit()
    
    return jsonify({"status": "success",
                    "message": "Chatroom created",
                    "chatroom_id": new_room.id}), 201
    
    
@auth_ct.route("/get_chatrooms", methods=["POST"])
#@jwt_required()
def get_chatrooms():
    post_data = request.get_json()
    
    username = post_data.get("username")
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"status": "failure", "message": "User not found"}), 404
    
    chatrooms = Chatroom.query.filter((Chatroom.user_1 == user.id) | 
                                      (Chatroom.user_2 == user.id)).all()
    
    result = []
    for room in chatrooms:
        other_id = room.user_2 if room.user_1 == user.id else room.user_1
        other_user = User.query.get(other_id)
        
        result.append({
            'chatroom_id': room.id,
            'with_user': other_user.username if other_user else "unknown",
            'with_user_id': other_id,
            'with_user_language': other_user.language if other_user else "unknown"
        })
        
    return jsonify({
        "status": "success",
        "message": "Get roomlist successfully",
        "username": user.username,
        "language": user.language,
        "chatrooms": result
    }), 200
    
    
@auth_ct.route("/get_messages", methods=["POST"])
def get_messages():
    post_data = request.get_json()
    
    user_id = post_data.get("user_id")
    chatroom_id = post_data.get("chatroom_id")
    
    user = User.query.filter_by(id=user_id).first()
    
    if not user:
        return jsonify({"status": "failure", "message": "User does not exist"}), 404
    
    chat_entries = Chat.query.filter_by(chatroom_id=chatroom_id).all()
    message_ids = [c.message_id for c in chat_entries]
    messages = Message.query.filter(Message.id.in_(message_ids)).order_by(Message.time.asc()).all()
    result = []
    for msg in messages:        
        result.append({
            'message_id': msg.id,
            'text_sender': msg.text_sender,
            'text_reciever': msg.text_reciever,
            'timestamp': msg.time.isoformat(),
            'sender_name': msg.sender_id,
            'receiver_name': msg.receiver_id,
        })
        
    return jsonify({
        "status": "success",
        "username": user_id,
        "chatroom_id": chatroom_id,
        "messages": "Fetch messages successfully",
        "messages": result
    }), 200
    