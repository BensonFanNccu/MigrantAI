from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from flask_jwt_extended import JWTManager

db       = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")
jwt = JWTManager()

def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or 'config.DefaultConfig')

    db.init_app(app)
    socketio.init_app(app)
    jwt.init_app(app)

    # register REST blueprints
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    
    from .api.user import auth_ur
    app.register_blueprint(auth_ur, url_prefix='/api/user')
    
    from .api.chat import auth_ct
    app.register_blueprint(auth_ct, url_prefix='/api/chat')
    
    # register DB
    from . import models
    with app.app_context():
        db.create_all()

    # register Socket.IO events
    from .chat.events import register_chat_handlers
    register_chat_handlers(socketio)

    return app
