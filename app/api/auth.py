from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from app import db
from app.models import User, Chatroom


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    post_data = request.get_json()
    
    username = post_data.get("username")
    password = post_data.get("password")
    language = post_data.get("language")
    identity = post_data.get("identity")
    
    if User.query.filter((User.username == username)).first():
        return jsonify({"status": "failure", "message": "Username already exists"}), 409
    
    hashed_password = generate_password_hash(password)
    new_user = User(username = username,
                    password=hashed_password,
                    language = language,
                    identity = identity)
    db.session.add(new_user)
    db.session.commit()
    

    return jsonify({"status": "success", "message": "Registered successfully"}), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    post_data = request.get_json()
    
    username = post_data.get("username")
    password = post_data.get("password")
    
    user = User.query.filter_by(username=username).first()
    
    if not user or not check_password_hash(user.password, password):
        return jsonify({"status": "failure", "message": "Wrong username or password"}), 401
    
    access_token = create_access_token(identity=user.id)
    
    return jsonify({"status": "success", 
                    "message": "Login successfully", 
                    "access_token": access_token}), 201


@auth_bp.route("/logout", methods=["POST"])
def logout():
    return jsonify({"status": "success", "message": 'Logged out successfully'}), 200    