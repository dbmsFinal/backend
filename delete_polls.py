from ORM import app, Poll, db
from flask_login import login_required, current_user
from flask import jsonify

@app.route('/delete_poll/<int:poll_id>', methods=['DELETE'])
@login_required
def delete_poll(poll_id):
    poll = Poll.query.get(poll_id)

    if not poll:
        return jsonify({"error": "Poll not found."}), 404

    if poll.creator_id != current_user.user_id or poll.is_approved:
        return jsonify({"error": "Unauthorized operation."}), 403

    db.session.delete(poll)
    db.session.commit()

    return jsonify({"message": "Poll deleted successfully."}), 200

if __name__ == "__main__":
    app.run(debug=True)