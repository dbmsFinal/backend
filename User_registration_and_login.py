from ORM import app, db, User, login_manager
from flask import request, jsonify
import re
from sqlalchemy.exc import SQLAlchemyError
from flask_login import login_user


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    # 檢查是否有漏填資料
    if not all(key in data for key in ("username", "email", "password")):
        return jsonify({
            "error": "Missing fields at username, email or password. Please enter again."
        }), 400
    
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    # 利用正則表達式檢查email形式是否符合
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({
                "error": "Invalid email format."
        }), 400
    
    # 檢查db是否有此email的用戶
    user = User.query.filter_by(email=email).first()

    if user:
        return jsonify({
                "error": "Email already exists."
        }), 400
    
    new_user = User(username=username, email=email, password=password)
    db.session.add(new_user)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
                "error": "Database error."
        }), 500
    
    return jsonify({
            "message": "Registered Successfully."
    }), 201


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    # 利用正則表達式檢查email形式是否符合
    if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
        return jsonify({
                "error": "Invalid email format."
        }), 400

    # 檢查是否有輸入信箱及密碼
    if not email or not password:
        return jsonify({
                "error": "Email or password not provided."
        }), 400

    try:
        user = User.query.filter_by(email=email).first()
    except SQLAlchemyError:
        return jsonify({
                "error": "Database error."
        }), 500
     
    if not user:
        return jsonify({
                "error": "Login failed. The email hasn't been registered."
            }), 401
    
    if user.password != password:
        return jsonify({
                "error": "Login failed. The password is not correct."
        }), 401

    login_user(user)
    return jsonify({
            "message": "Logged in successfully."
    }), 200

if __name__ == '__main__':
    app.run()