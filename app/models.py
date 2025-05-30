from . import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(30), nullable=False)
    language = db.Column(db.String(10), nullable=False)
    identity = db.Column(db.String(10), nullable=False)
    
    
class Chatroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_1 = db.Column(db.String(10), nullable=False)
    user_2 = db.Column(db.String(10), nullable=False)
    
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text_sender = db.Column(db.String(1000))
    text_reciever = db.Column(db.String(1000))
    time = db.Column(db.TIMESTAMP(True), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    
class Chat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(db.Integer, db.ForeignKey('message.id'), nullable=False)
    chatroom_id = db.Column(db.Integer, db.ForeignKey('chatroom.id'), nullable=False)  