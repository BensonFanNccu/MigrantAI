import os

class DefaultConfig:
    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key')

    # SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///chat.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

   
