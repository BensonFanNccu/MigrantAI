from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO

db       = SQLAlchemy()
socketio = SocketIO(cors_allowed_origins="*")

def create_app(config_object=None):
    app = Flask(__name__)
    app.config.from_object(config_object or 'config.DefaultConfig')

    db.init_app(app)
    socketio.init_app(app)

    # register REST blueprints
    from .api.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    # register Socket.IO events
    from .chat.events import register_chat_handlers
    register_chat_handlers(socketio)

    return app
