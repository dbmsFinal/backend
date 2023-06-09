from ORM import app, db, User, Poll
from flask import request, jsonify, Blueprint
from flask_login import login_user, login_required, current_user


bp = Blueprint('admin', __name__)


@bp.route('/admin/getAllUsers_unactive', methods=['GET'])
@login_required
def get_all_user_unactive():
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401
    users = User.query.filter_by(is_active=0).all()
    return jsonify({"users": [user_to_dict(user)  for user in users]}), 200
@bp.route('/admin/getAllUsers_active', methods=['GET'])
@login_required
def get_all_user():
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401
    users = User.query.filter_by(is_active=1).all()
    return jsonify({"users": [user_to_dict(user)  for user in users]}), 200

# 網站管理員可以審核和管理用戶創建的公投，如審核不適當的內容、刪除違規公投等。
@bp.route('/admin/approve_poll', methods=['POST'])
@login_required
def approve_poll():
    # 若非管理員，則回傳 "error":"You are not admin."
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401

    data = request.get_json()
    poll_id_to_approve = data['poll_id_to_approve']
    poll_to_approve = Poll.query.get(poll_id_to_approve)

    # 如果公投 id 不存在，則回傳 "error": "Poll {id} doesn't exist."
    if not poll_to_approve: return jsonify({"error":f"Poll {poll_id_to_approve} doesn't exist."}), 400
    
    # 修改 Poll.is_approved 為 1，並回傳 Poll is approved
    poll_to_approve.is_approved = 1
    db.session.commit()
    return jsonify({"message":f"Poll {poll_id_to_approve} '{poll_to_approve.title}' is approved."}), 200

@bp.route('/admin/disapprove_poll', methods=['POST'])
@login_required
def disapprove_poll():
    # 若非管理員，則回傳 "error":"You are not admin."
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401

    data = request.get_json()
    poll_id_to_disapprove = data['poll_id_to_disapprove']
    poll_to_disapprove = Poll.query.get(poll_id_to_disapprove)
    
    # 如果公投 id 不存在，則回傳 "error": "Poll {id} doesn't exist."
    if not poll_to_disapprove: return jsonify({"error":f"Poll {poll_id_to_disapprove} doesn't exist."}), 400
    
    # 修改 Poll.is_approved 為 0，並回傳 Poll is disapproved
    poll_to_disapprove.is_approved = 0
    db.session.commit()
    return jsonify({"message":f"Poll {poll_id_to_disapprove} '{poll_to_disapprove.title}' is disapproved."}), 200

@bp.route('/admin/delete_comment', methods=['POST'])
@login_required
def delete_comment():
    pass

# 網站管理員可以管理用戶帳戶，如禁用違規用戶。
@bp.route('/admin/ban_user', methods=['POST'])
@login_required
def ban_user():
    # 若非管理員，則回傳 "error":"You are not admin."
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401
    
    data = request.get_json()
    user_id_to_disable = data['user_id_to_disable']
    user_to_disable = User.query.get(user_id_to_disable)
   
    if user_to_disable.user_id == 4: return jsonify({"error":"You can't ban admin."}), 401
    # 如果用戶 id 不存在，則回傳 "error": "User {id} doesn't exist."
    if not user_to_disable: return jsonify({"error":f"User {user_id_to_disable} doesn't exist."}), 400
    
    # 修改 User.is_active 為 0，並回傳 User is disabled
    user_to_disable.is_active = 0
    db.session.commit()
    return jsonify({"message":f"User {user_id_to_disable} '{user_to_disable.username}' is disabled."}), 200

@bp.route('/admin/reactivate_user', methods=['POST'])
@login_required
def reactivate_user():
    # 若非管理員，則回傳 "error":"You are not admin."
    if current_user.email != 'admin@nccu.edu.tw': return jsonify({"error":"You are not admin."}), 401

    data = request.get_json()
    user_id_to_reactivate = data['user_id_to_reactivate']
    user_to_reactivate = User.query.get(user_id_to_reactivate)

    # 如果用戶 id 不存在，則回傳 "error": "User {id} doesn't exist."
    if not user_to_reactivate: return jsonify({"error":f"User {user_id_to_reactivate} doesn't exist."}), 400
    
    # 修改 User.is_active 為 0，並回傳 User is disabled
    user_to_reactivate.is_active = 1
    db.session.commit()
    return jsonify({"message":f"User {user_id_to_reactivate} '{user_to_reactivate.username}' is reactivated."}), 200


def user_to_dict(user):
    return {
        'user_id': user.user_id,
        "is_active": user.is_active,
        'username': user.username,
       
    }
if __name__ == '__main__':
    app.run(debug=True)