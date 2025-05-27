from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from app import db
from app.models import User


auth_ur = Blueprint("user", __name__)


@auth_ur.route("/edit", methods=["POST"])
#@jwt_required()
def edit():
    #user_id = get_jwt_identity()
    post_data = request.get_json()
    
    username = post_data.get("username")
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"status": "failure", "message": "User not found"}), 404
    
    username = post_data.get("username")
    password = post_data.get("password")
    language = post_data.get("language")
    identity = post_data.get("identity")
    
    if username and username != user.username:
        if User.query.filter_by(username=username).first():
            return jsonify({"status": "failure", "message": "Username already exists"}), 409
        user.username = username
        
    user.password = generate_password_hash(password)
    user.language = language
    user.identity = identity
    
    db.session.commit()
    
    return jsonify({"status": "success", "message": "Edited successfully"}), 201


@auth_ur.route("/profile", methods=["GET"])
#@jwt_required()
def profile():
    #user_id = get_jwt_identity()
    post_data = request.get_json()
    
    username = post_data.get("username")
    user = User.query.filter_by(username=username).first()
    
    if not user:
        return jsonify({"status": "failure", "message": "User not found"}), 404
    
    return jsonify({"status": "success", 
                    "message": "Get profile successfully",
                    "language": user.language,
                    "identity": user.identity}), 200